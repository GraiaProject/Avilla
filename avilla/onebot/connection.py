import asyncio
from abc import ABCMeta, abstractmethod
from asyncio import Future
from contextlib import ExitStack, suppress
import traceback
from typing import TYPE_CHECKING, Callable, Dict, Optional, cast, final

from loguru import logger

from avilla.core.message import Message
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import message as message_selector
from avilla.core.stream import Stream
from avilla.core.transformers import u8_string
from avilla.core.typing import STRUCTURE
from avilla.core.utilles import random_string
from avilla.io.common.http import WebsocketClient, WebsocketConnection
from avilla.onebot.config import OnebotConnectionConfig, OnebotWsClientConfig
from avilla.core.context import ctx_avilla, ctx_protocol, ctx_relationship

if TYPE_CHECKING:
    from .service import OnebotService


class OnebotConnection(metaclass=ABCMeta):
    account: entity_selector
    service: "OnebotService"
    config: OnebotConnectionConfig

    @abstractmethod
    async def maintask(self):
        raise NotImplementedError

    @abstractmethod
    async def send(self, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def action(self, action: str, data: dict, timeout: float = None) -> dict:
        raise NotImplementedError


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
            @self.ws_connection.on_received
            async def on_received_data(connection: WebsocketConnection, stream: Stream[bytes]):
                data = await stream.transform(u8_string).transform(
                    cast(Callable[[str], Dict], self.config.data_parser)
                ).unwrap()
                if "echo" in data:
                    logger.debug(f"received echo: {data}")
                    if data["echo"] in self.requests:
                        self.requests[data["echo"]].set_result(data)
                    else:
                        logger.warning(
                            f"Received echo message {data['echo']} but not found in requests: {data}"
                        )
                else:
                    #logger.debug(f"received event: {data}")
                    with ExitStack() as stack:
                        stack.enter_context(ctx_avilla.use(avilla))
                        stack.enter_context(ctx_protocol.use(self.service.protocol))
                        event = await self.service.protocol.parse_event(data)
                        if event:
                            broadcast.postEvent(event)

            #await avilla.sigexit.wait()

    async def send(self, data: dict):
        if not self.ws_connection:
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
