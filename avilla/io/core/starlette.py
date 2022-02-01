import asyncio
from contextlib import asynccontextmanager
import json
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, Type, Union, cast

from graia.broadcast.utilles import Ctx
from loguru import logger
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from avilla.core import LaunchComponent, Service
from avilla.core.selectors import entity as entity_selector
from avilla.core.stream import Stream
from avilla.core.transformers import u8_encode
from avilla.core.utilles import random_string
from avilla.io.common.http import (
    HTTP_METHODS,
    ASGIHandlerProvider,
    HttpServer,
    HttpServerRequest,
    WebsocketConnection,
    WebsocketServer,
)

if TYPE_CHECKING:
    from avilla.core import Avilla


class StarletteHttpRequest(HttpServerRequest):
    def __init__(self, request: Request):
        self.request = request

    async def read(self) -> Stream[bytes]:
        return Stream(await self.request.body())

    async def response(self, resp: Any, status: int = 200) -> None:
        if isinstance(resp, (dict, list)):
            resp = JSONResponse(resp, status_code=status)
        elif isinstance(resp, str):
            resp = PlainTextResponse(resp, status_code=status)
        elif isinstance(resp, bytes):
            resp = Response(resp, status_code=status)
        else:
            raise TypeError(f"Unsupported response type: {type(resp)}")
        await self.request.app.send_response(self.request, resp)

    async def cookies(self) -> Dict[str, str]:
        return self.request.cookies

    async def headers(self) -> Dict[str, str]:
        return dict(self.request.headers)

    @property
    def url(self):
        return self.request.url

    @property
    def method(self):
        return self.request.method

    @property
    def path(self):
        return self.request.url.path


class StarletteWebsocketServerConnection(WebsocketConnection):
    server_mode = True

    websocket_ctx: Ctx["WebSocket"]

    def __init__(self):
        self.before_accept_callbacks = []
        self.connected_callbacks = []
        self.received_callbacks = []
        self.close_callbacks = []
        self.websocket_ctx = Ctx(f"starlette_ws_{random_string()}")

    async def send(
        self,
        data: Union[Stream[Union[bytes, str, dict, list]], bytes, str, dict, list],
        *,
        json_serializer: Callable[[Union[dict, list]], str] = None,
    ) -> None:
        ws = self.websocket_ctx.get()
        if ws is None:
            raise RuntimeError("Websocket connection not prepared")
        if isinstance(data, Stream):
            data = await data.unwrap()
        if isinstance(data, (dict, list)):
            await ws.send_json(data)
        elif isinstance(data, str):
            await ws.send_text(data)
        elif isinstance(data, bytes):
            await ws.send_bytes(data)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

    async def close(self, code: int = 1000, message: bytes = b"") -> None:
        ws = self.websocket_ctx.get()
        if ws is None:
            raise RuntimeError("Websocket connection not prepared")
        if message:
            await ws.send_bytes(message)
        await ws.close(code)

    async def accept(self) -> None:
        ws = self.websocket_ctx.get()
        if ws is None:
            raise RuntimeError("Websocket connection not prepared")
        await ws.accept()

    def headers(self) -> Dict[str, str]:
        ws = self.websocket_ctx.get()
        if ws is None:
            raise RuntimeError("Websocket connection not prepared")
        return dict(ws.headers)

    async def ping(self) -> None:
        raise NotImplementedError

    async def pong(self) -> None:
        raise NotImplementedError

    @property
    def client(self) -> Tuple[str, int]:
        ws = self.websocket_ctx.get()
        if ws is None:
            raise RuntimeError("Websocket connection not prepared")
        return (ws.client.host, ws.client.port)


class StarletteServer(HttpServer, WebsocketServer, ASGIHandlerProvider):
    starlette: Starlette
    service: "StarletteService"

    def __init__(self, service: "StarletteService", starlette: Starlette):
        self.service = service
        self.starlette = starlette

        super().__init__()

    def get_asgi_handler(self):
        return self.starlette

    def http_listen(
        self,
        path: str,
        methods: List[HTTP_METHODS] = None,
    ):
        methods = methods or ["get", "post", "put", "delete"]

        def wrapper(callback: Callable[[StarletteHttpRequest], Any]):
            async def _wrapper(request: Request):
                if request.method not in methods:
                    return JSONResponse({"message": "Method not allowed"}, status_code=405)

                return await callback(StarletteHttpRequest(request))

            self.starlette.add_route(path, _wrapper)

        return wrapper

    @asynccontextmanager
    async def websocket_listen(self, path: str):
        ws = StarletteWebsocketServerConnection()

        async def connection_wrapper(conn: WebSocket):
            with ws.websocket_ctx.use(conn):
                await asyncio.wait([cb(ws) for cb in ws.before_accept_callbacks])
                # 不合法直接 close.
                # 我记得 accept 之前不能 send, 所以别想啦。
                if conn.application_state == WebSocketState.DISCONNECTED:
                    return
                await conn.accept()
                await asyncio.wait([cb(ws) for cb in ws.connected_callbacks])
                # 在这里可以想。
                avilla = self.service.avilla
                try:
                    while not avilla.sigexit.is_set():
                        msg = await conn.receive()
                        if msg['type'] == "websocket.receive":
                            await asyncio.wait([cb(ws, Stream(msg['text'])) for cb in ws.received_callbacks])
                        elif msg['type'] == "websocket.disconnect":
                            break
                except WebSocketDisconnect:
                    await asyncio.wait([cb(ws) for cb in ws.close_callbacks])
                logger.warning(f"Websocket connection closed: {path}, {conn.client}")

        self.starlette.websocket_route(path)(connection_wrapper)
        yield ws


class StarletteService(Service):
    supported_interface_types = ({StarletteServer, HttpServer, WebsocketServer, ASGIHandlerProvider}, {})

    avilla: "Avilla"

    starlette: Starlette

    def __init__(self, starlette: Starlette = None) -> None:
        self.starlette = starlette or Starlette()
        super().__init__()

    def get_interface(self, interface_type: Type[StarletteServer]) -> StarletteServer:
        if issubclass(interface_type, (HttpServer, WebsocketServer, ASGIHandlerProvider)):
            return StarletteServer(self, self.starlette)
        raise ValueError(f"unsupported interface type {interface_type}")

    def get_status(self, entity: entity_selector = None):
        if entity is None:
            return self.status
        if entity not in self.status:
            raise KeyError(f"{entity} not in status")
        return self.status[entity]

    async def launch_prepare(self, avilla: "Avilla"):
        self.avilla = avilla

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent("http.universal_server", set(), prepare=self.launch_prepare)
