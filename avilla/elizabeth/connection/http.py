from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional

from aiohttp import FormData
from graia.amnesia.builtins.aiohttp import AiohttpClientInterface
from graia.amnesia.json import Json
from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.http import AbstractServerRequestIO, HttpEndpoint
from graia.amnesia.transport.common.http.extra import HttpRequest
from graia.amnesia.transport.common.server import AbstractRouter
from launart import Launart
from launart.utilles import wait_fut
from loguru import logger

from ..exception import InvalidSession
from . import ElizabethConnection
from .config import HttpClientConfig, HttpServerConfig
from .util import CallMethod, get_router, validate_response

if TYPE_CHECKING:
    from avilla.elizabeth.protocol import ElizabethProtocol


class HttpServerConnection(ElizabethConnection[HttpServerConfig], Transport):
    """HTTP 服务器连接"""

    dependencies = frozenset([AbstractRouter])

    def __init__(self, protocol: ElizabethProtocol, config: HttpServerConfig) -> None:
        super().__init__(protocol, config)
        self.handlers[HttpEndpoint(self.config.path, ["POST"])] = self.__class__.handle_request

    async def handle_request(self, io: AbstractServerRequestIO):
        req: HttpRequest = await io.extra(HttpRequest)
        if req.headers.get("qq") != str(self.config.account):
            return
        for k, v in self.config.headers.items():
            if req.headers.get(k) != v:
                return "Authorization failed", {"status": 401}
        data = Json.deserialize((await io.read()).decode("utf-8"))
        assert isinstance(data, dict)
        self.status.connected = True
        self.status.alive = True
        self.register_account()  # LINK: hot registration
        try:
            event, context = await self.protocol.parse_event(self.account, data)
            self.protocol.post_event(event, context)
        except Exception:
            logger.exception("error on parsing event: ", data)
        return {"command": "", "data": {}}

    async def launch(self, mgr: Launart) -> None:
        router = get_router(mgr)
        router.use(self)


class HttpClientConnection(ElizabethConnection[HttpClientConfig]):
    """HTTP 客户端连接"""

    dependencies = frozenset([AiohttpClientInterface])
    http_interface: AiohttpClientInterface

    def __init__(self, protocol: ElizabethProtocol, config: HttpClientConfig) -> None:
        super().__init__(protocol, config)
        self.is_hook: bool = False

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        data: Optional[Any] = None,
        json: Optional[dict] = None,
    ) -> Any:
        if data and isinstance(data, dict):
            form = FormData(quote_fields=False)
            for k, v in data.items():
                form.add_field(k, **v) if isinstance(v, dict) else form.add_field(k, v)
            data = form
        rider = await self.http_interface.request(method, url, params=params, data=data, json=json)
        byte_data = await rider.io().read()
        result = Json.deserialize(byte_data.decode("utf-8"))
        return validate_response(result)

    async def http_auth(self) -> None:
        data = await self.request(
            "POST",
            self.config.get_url("verify"),
            json={"verifyKey": self.config.verify_key},
        )
        session_key = data["session"]
        await self.request(
            "POST",
            self.config.get_url("bind"),
            json={"qq": self.config.account, "sessionKey": session_key},
        )
        self.status.session_key = session_key

    async def call(self, command: str, method: CallMethod, params: Optional[dict] = None) -> Any:
        params = params or {}
        command = command.replace("_", "/")
        while not self.status.connected:
            await self.status.wait_for_update()
        if not self.status.session_key:
            await self.http_auth()
        try:
            if method in ("get", "fetch"):
                return await self.request("GET", self.config.get_url(command), params=params)
            elif method in ("post", "update"):
                return await self.request("POST", self.config.get_url(command), json=params)
            elif method == "multipart":
                return await self.request("POST", self.config.get_url(command), data=params)
        except InvalidSession:
            self.status.session_key = None
            raise

    @property
    def stages(self):
        return set() if self.is_hook else {"blocking"}

    async def launch(self, mgr: Launart) -> None:
        self.http_interface = mgr.get_interface(AiohttpClientInterface)
        if self.is_hook:
            return
        async with self.stage("blocking"):
            while not mgr.launchables["elizabeth.service"].status.finished:
                try:
                    if not self.status.session_key:
                        logger.info("HttpClient: authenticate", style="dark_orange")
                        await self.http_auth()
                    self.register_account()  # LINK: hot registration
                    data = await self.request(
                        "GET",
                        self.config.get_url("fetchMessage"),
                        {"sessionKey": self.status.session_key, "count": 10},
                    )
                    self.status.alive = True
                except Exception as e:
                    self.status.session_key = None
                    self.status.alive = False
                    logger.exception(e)
                    continue
                assert isinstance(data, list)
                for event_data in data:
                    try:
                        event, context = await self.protocol.parse_event(self.account, event_data)
                        self.protocol.post_event(event, context)
                    except Exception:
                        logger.exception("error on parsing event: ", event_data)
                await wait_fut(
                    [asyncio.sleep(0.5), mgr.status.wait_for_sigexit()],
                    return_when=asyncio.FIRST_COMPLETED,
                )
