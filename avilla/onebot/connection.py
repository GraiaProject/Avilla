import asyncio
from abc import ABCMeta, abstractmethod
from asyncio import Future
from typing import TYPE_CHECKING, Dict, Optional, cast, final

from loguru import logger

from avilla.core.message import Message
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import message as message_selector
from avilla.core.transformers import u8_string
from avilla.core.typing import STRUCTURE
from avilla.core.utilles import random_string
from avilla.io.common.http import WebsocketClient, WebsocketConnection
from avilla.onebot.config import OnebotConnectionConfig, OnebotWsClientConfig

if TYPE_CHECKING:
    from .service import OnebotService


class OnebotConnection(metaclass=ABCMeta):
    account: entity_selector
    service: OnebotService
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
    service: OnebotService
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
            while not self.service.protocol.avilla.sigexit.is_set():
                try:
                    stream = await self.ws_connection.receive()
                    data = await stream.transform(u8_string).transform(self.config.data_parser).unwrap()
                    data = cast(Dict, data)
                    if "echo" in data:
                        if data["echo"] in self.requests:
                            self.requests[data["echo"]].set_result(data)
                        else:
                            logger.warning(
                                f"Received echo message {data['echo']} but not found in requests: {data}"
                            )
                    else:
                        post_type: str = data["post_type"]
                        if post_type == "message":
                            message_type = data["message_type"]

                        elif post_type == "notice":
                            notice_type = data["notice_type"]
                        elif post_type == "request":
                            request_type = data["request_type"]
                        elif post_type == "meta_event":
                            meta_event_type = data["meta_event_type"]
                            sub_type = data.get("sub_type")
                except:
                    raise  # TODO： error handle

    async def send(self, data: dict):
        if not self.ws_connection:
            raise RuntimeError("Not connected")
        await self.ws_connection.send(self.config.data_serializer(data).encode())

    async def action(self, action: str, data: dict, timeout: float = None):
        request_id = random_string()
        self.requests[request_id] = asyncio.get_event_loop().create_future()
        try:
            await self.send({"action": action, "params": data, "echo": request_id})
            return await asyncio.wait_for(self.requests[request_id], timeout)
        finally:
            del self.requests[request_id]
