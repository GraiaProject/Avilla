import asyncio
import hmac
import json
import traceback
from abc import ABCMeta, abstractmethod
from asyncio import Future
from contextlib import ExitStack, suppress
from functools import partial
from typing import TYPE_CHECKING, Callable, Dict, Literal, Optional, Union, cast, final

from loguru import logger

from avilla.core.context import ctx_avilla, ctx_protocol
from avilla.core.message import Message
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import message as message_selector
from avilla.core.stream import Stream
from avilla.core.transformers import u8_string
from avilla.core.typing import STRUCTURE
from avilla.core.utilles import random_string
from avilla.io.common.http import (
    HttpClient,
    HttpServer,
    HttpServerRequest,
    WebsocketClient,
    WebsocketConnection,
    WebsocketServer,
)
from avilla.onebot.config import (
    OnebotConnectionConfig,
    OnebotHttpClientConfig,
    OnebotHttpServerConfig,
    OnebotWsClientConfig,
    OnebotWsServerConfig,
)
from avilla.onebot.utilles import raise_for_obresp

if TYPE_CHECKING:
    from .service import OnebotService

OnebotConnectionRole = Literal["action", "event", "universal"]


class OnebotConnection(metaclass=ABCMeta):
    account: entity_selector
    service: "OnebotService"
    config: OnebotConnectionConfig

    @abstractmethod
    async def maintask(self):
        raise NotImplementedError

    @abstractmethod
    async def send(self, data: dict) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def action(self, action: str, data: dict, timeout: float = None) -> dict:
        raise NotImplementedError


class OnebotHttpClient(OnebotConnection):
    http_client: HttpClient
    account: entity_selector
    service: "OnebotService"
    config: OnebotHttpClientConfig

    def __init__(
        self,
        http_client: HttpClient,
        account: entity_selector,
        service: "OnebotService",
        config: OnebotHttpClientConfig,
    ):
        self.http_client = http_client
        self.account = account
        self.service = service
        self.config = config
        self.requests = {}

    async def maintask(self):
        self.service.set_status(self.account, True, "ok")
        logger.info(f"onebot http client for {self.account} connected")

        while not self.service.protocol.avilla.sigexit.is_set():
            try:
                async with self.http_client.get(self.config.url / "get_status") as response:
                    data = await (await response.read()).transform(u8_string).transform(json.loads).unwrap()
                    raise_for_obresp(data)
                    if not data["data"]["online"] or not data["data"]["good"]:
                        raise RuntimeError("onebot remote is offline")
            except Exception as e:
                self.service.set_status(self.account, False, "offline")
                logger.warning(f"onebot http client for {self.account} disconnected")
                # raise e # 在？这里 raise 什么意思？
            else:
                await asyncio.sleep(30)

    async def send(self, data: dict) -> Optional[dict]:
        async with self.http_client.post(
            self.config.url / data["action"],
            data["params"],
            headers=(
                {"Authorization": f"Bearer {self.config.access_token}"} if self.config.access_token else {}
            ),
        ) as response:
            return await (await response.read()).transform(u8_string).transform(json.loads).unwrap()

    async def action(self, action: str, data: dict, timeout: float = None) -> dict:
        return await asyncio.wait_for(self.send({"action": action, "params": data}), timeout) or {}


class OnebotWsClient(OnebotConnection):
    ws_client: WebsocketClient
    ws_connection: Optional[WebsocketConnection] = None
    account: entity_selector
    service: "OnebotService"
    config: OnebotWsClientConfig

    requests: Dict[str, "Future[dict]"]

    def __init__(
        self,
        ws_client: WebsocketClient,
        account: entity_selector,
        service: "OnebotService",
        config: OnebotWsClientConfig,
    ):
        self.ws_client = ws_client
        self.account = account
        self.service = service
        self.config = config
        self.requests = {}

    async def maintask(self):
        async with self.ws_client.websocket_connect(
            self.config.url,
            headers=(
                {"Authorization": f"Bearer {self.config.access_token}"} if self.config.access_token else {}
            ),
        ) as self.ws_connection:
            # 这里应该是放在 / (即 /api 与 /event 的总集上.)
            # TODO: 好了, 连上了，就该开始了。
            avilla = self.service.protocol.avilla
            broadcast = avilla.broadcast

            @self.ws_connection.on_connected
            async def on_connected(_):
                self.service.set_status(self.account, True, "ok")
                self.service.trig_available_waiters(self.account)

            @self.ws_connection.on_close
            async def on_close(_):
                self.service.set_status(self.account, False, "offline")
                logger.warning(f"onebot websocket client for {self.account} disconnected")

            @self.ws_connection.on_received
            async def on_received_data(connection: WebsocketConnection, stream: Stream[Union[dict, list,bytes,str]]):
                data = (
                    await stream.transform(u8_string, bytes)  # type: ignore
                    .transform(cast(Callable[[str], Dict], self.config.data_parser), str)
                    .unwrap()
                )
                if "echo" in data:
                    logger.debug(f"received echo: {data}")
                    if data["echo"] in self.requests:
                        self.requests[data["echo"]].set_result(data)
                    else:
                        logger.warning(
                            f"Received echo message {data['echo']} but not found in requests: {data}"
                        )
                else:
                    # logger.debug(f"received event: {data}")
                    event = await self.service.protocol.parse_event(data)
                    if event:
                        with ExitStack() as stack:
                            stack.enter_context(ctx_avilla.use(avilla))
                            stack.enter_context(ctx_protocol.use(self.service.protocol))
                            broadcast.postEvent(event)

            # await avilla.sigexit.wait()

    async def send(self, data: dict) -> Optional[dict]:
        if not self.ws_connection:  # not there, but "ws client" and "http client"
            raise RuntimeError("Not connected")
        await self.ws_connection.send(data)

    async def action(self, action: str, params: dict, timeout: float = None):
        request_id = random_string()
        self.requests[request_id] = asyncio.get_running_loop().create_future()
        try:
            await self.send({"action": action, "params": params, "echo": request_id})
            return await asyncio.wait_for(self.requests[request_id], timeout)
        finally:
            del self.requests[request_id]


class OnebotHttpServer(OnebotConnection):
    http_server: HttpServer
    account: entity_selector
    service: "OnebotService"
    config: OnebotHttpServerConfig

    def __init__(
        self,
        http_server: HttpServer,
        account: entity_selector,
        service: "OnebotService",
        config: OnebotHttpServerConfig,
    ):
        self.http_server = http_server
        self.account = account
        self.service = service
        self.config = config

    async def maintask(self):
        self.http_server.http_listen(self.config.api_root, ["post"])(self.service.http_server_on_received)

    async def send(self, data: dict) -> Optional[dict]:
        raise NotImplementedError

    async def action(self, action: str, data: dict, timeout: float = None) -> dict:
        raise NotImplementedError


class OnebotWsServer(OnebotConnection):
    ws_server: WebsocketServer
    account: entity_selector
    service: "OnebotService"
    config: OnebotWsServerConfig

    universal_connection: Optional[WebsocketConnection] = None
    api_connection: Optional[WebsocketConnection] = None
    event_connection: Optional[WebsocketConnection] = None

    requests: Dict[str, "Future[dict]"]

    def __init__(
        self,
        ws_server: WebsocketServer,
        account: entity_selector,
        service: "OnebotService",
        config: OnebotWsServerConfig,
    ):
        self.ws_server = ws_server
        self.account = account
        self.service = service
        self.config = config
        self.requests = {}

    async def maintask(self):
        async with self.ws_server.websocket_listen(self.config.api_root + self.config.universal) as conn:
            conn.before_accept(partial(self.service.ws_server_before_accept, self))
            conn.on_connected(partial(self.service.ws_server_on_connected, self))
            conn.on_received(partial(self.service.ws_server_on_received, self))
            conn.on_close(partial(self.service.ws_server_on_close, self))
            self.universal_connection = conn

    async def send(self, data: dict) -> Optional[dict]:
        if self.universal_connection:
            await self.universal_connection.send(data)
        elif self.api_connection:
            await self.api_connection.send(data)
        else:
            raise RuntimeError("Not connected")

    async def action(self, action: str, params: dict, timeout: float = None):
        request_id = random_string()
        self.requests[request_id] = asyncio.get_running_loop().create_future()
        try:
            await self.send({"action": action, "params": params, "echo": request_id})
            return await asyncio.wait_for(self.requests[request_id], timeout)
        finally:
            del self.requests[request_id]
