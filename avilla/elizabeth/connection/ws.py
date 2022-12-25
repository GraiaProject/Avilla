from __future__ import annotations

import asyncio
import secrets
from typing import TYPE_CHECKING, Any, Dict, MutableMapping, Optional, TypeVar
from weakref import WeakValueDictionary

from graia.amnesia.builtins.aiohttp import AiohttpClientInterface
from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.client import AbstractClientInterface
from graia.amnesia.transport.common.http.extra import HttpRequest
from graia.amnesia.transport.common.websocket import (
    AbstractWebsocketIO,
    WebsocketCloseEvent,
    WebsocketConnectEvent,
    WebsocketEndpoint,
    WebsocketReceivedEvent,
    WebsocketReconnect,
    WSConnectionAccept,
    WSConnectionClose,
)
from graia.amnesia.transport.common.websocket.shortcut import data_type, json_require
from graia.amnesia.transport.utilles import TransportRegistrar
from launart import Launart
from launart.utilles import wait_fut
from loguru import logger
from yarl import URL

from . import ElizabethConnection
from .config import WebsocketClientConfig, WebsocketServerConfig
from .util import CallMethod, get_router, validate_response

if TYPE_CHECKING:
    from avilla.elizabeth.protocol import ElizabethProtocol

t = TransportRegistrar()

T_WebsocketConfig = TypeVar("T_WebsocketConfig", WebsocketClientConfig, WebsocketServerConfig)


@t.apply
class BaseWebsocketConnection(Transport, ElizabethConnection[T_WebsocketConfig]):
    ws_io: Optional[AbstractWebsocketIO]
    futures: MutableMapping[str, asyncio.Future]
    config: T_WebsocketConfig

    def __init__(self, protocol: ElizabethProtocol, config: T_WebsocketConfig) -> None:
        super().__init__(protocol, config)
        self.futures = WeakValueDictionary()

    @t.on(WebsocketReceivedEvent)
    @data_type(str)
    @json_require
    async def _(self, _: AbstractWebsocketIO, raw: Any) -> None:  # event pass and callback
        assert isinstance(raw, dict)
        if "code" in raw:  # something went wrong
            validate_response(raw)  # raise it
        sync_id: str = raw.get("syncId", "#")
        data = raw.get("data", None)
        data = validate_response(data, raising=False)
        if isinstance(data, Exception):
            if sync_id in self.futures:
                self.futures[sync_id].set_exception(data)
            return
        if "session" in data:
            self.status.session_key = data["session"]
            logger.success("Successfully got session key", style="green bold")
            self.register_account()  # LINK: hot registration
            return
        if sync_id in self.futures:
            self.futures[sync_id].set_result(data)
        elif "type" in data:
            self.status.alive = True
            try:
                event, context = await self.protocol.parse_event(self.account, data)
                self.protocol.post_event(event, context)
            except Exception:
                logger.exception("error on parsing event: ", data)
        else:
            logger.warning(f"Got unknown data: {raw}")

    @t.handle(WebsocketReconnect)
    async def _(self, _) -> bool:
        logger.warning("Websocket reconnecting in 5s...", style="dark_orange")
        await asyncio.sleep(5)
        logger.warning("Websocket reconnecting...", style="dark_orange")
        return True

    @t.on(WebsocketCloseEvent)
    async def _(self, _: AbstractWebsocketIO) -> None:
        self.status.session_key = None
        self.status.alive = False
        logger.info("Websocket connection closed", style="dark_orange")

    async def call(self, command: str, method: CallMethod, params: Optional[dict] = None) -> Any:
        params = params or {}
        sync_id: str = secrets.token_urlsafe(12)
        fut = asyncio.get_running_loop().create_future()
        content: Dict[str, Any] = {"syncId": sync_id, "command": command, "content": params or {}}
        if method == "fetch":
            content["subCommand"] = "get"
        elif method == "update":
            content["subCommand"] = "update"
        elif method == "multipart":
            if self.http_conn:
                return await self.http_conn.call(command, method, params)
            raise NotImplementedError(
                f"Connection {self} can't perform {command!r}, consider configuring a HttpClientConnection?"
            )
        self.futures[sync_id] = fut
        await self.status.wait_for_available()
        assert self.ws_io
        await self.ws_io.send(content)
        return await fut


t = TransportRegistrar()


@t.apply
class WebsocketServerConnection(BaseWebsocketConnection[WebsocketServerConfig]):
    """Websocket 服务器连接"""

    dependencies = frozenset([AbstractClientInterface])

    config: WebsocketServerConfig

    def __init__(self, protocol: ElizabethProtocol, config: WebsocketServerConfig) -> None:
        super().__init__(protocol, config)
        self.declares.append(WebsocketEndpoint(self.config.path))

    async def launch(self, mgr: Launart) -> None:
        router = get_router(mgr)
        router.use(self)

    @t.on(WebsocketConnectEvent)
    async def _(self, io: AbstractWebsocketIO) -> None:
        req: HttpRequest = await io.extra(HttpRequest)
        for k, v in self.config.headers.items():
            if req.headers.get(k) != v:
                return await io.extra(WSConnectionClose)
        for k, v in self.config.params.items():
            if req.query_params.get(k) != v:
                return await io.extra(WSConnectionClose)
        await io.extra(WSConnectionAccept)
        logger.info("WebsocketServer")
        await io.send(
            {
                "syncId": "#",
                "command": "verify",
                "content": {
                    "verifyKey": self.config.verify_key,
                    "sessionKey": None,
                    "qq": self.config.account,
                },
            }
        )
        self.ws_io = io


t = TransportRegistrar()


@t.apply
class WebsocketClientConnection(BaseWebsocketConnection[WebsocketClientConfig]):
    """Websocket 客户端连接"""

    dependencies = frozenset([AbstractClientInterface])
    http_interface: AiohttpClientInterface
    config: WebsocketClientConfig

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, mgr: Launart) -> None:
        self.http_interface = mgr.get_interface(AiohttpClientInterface)
        config = self.config
        async with self.stage("blocking"):
            rider = self.http_interface.websocket(
                str(URL(config.get_url("all")).with_query({"qq": config.account, "verifyKey": config.verify_key}))
            )
            await wait_fut(
                [rider.use(self), mgr.status.wait_for_sigexit()],
                return_when=asyncio.FIRST_COMPLETED,
            )

    @t.on(WebsocketConnectEvent)
    async def _(self, io: AbstractWebsocketIO) -> None:  # start authenticate
        self.ws_io = io
        self.status.alive = True
