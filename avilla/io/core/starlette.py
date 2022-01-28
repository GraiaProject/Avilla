import asyncio
from contextlib import ExitStack, asynccontextmanager
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, List, Type, Union

from graia.broadcast.utilles import Ctx
from loguru import logger
from pydantic.main import BaseModel
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from avilla.core import LaunchComponent, Service
from avilla.core.selectors import entity as entity_selector
from avilla.core.service.session import BehaviourSession
from avilla.core.stream import Stream
from avilla.core.utilles import random_string
from avilla.io.common.http import (
    HTTP_METHODS,
    ASGIHandlerProvider,
    HttpServer,
    HttpServerRequest,
    WebsocketConnection,
    WebsocketServer,
)


class StarletteHttpRequest(HttpServerRequest):
    def __init__(self, request: Request):
        self.request = request

    async def read(self) -> Stream[bytes]:
        return Stream(await self.request.body())

    async def response(self, resp: Response) -> None:
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
        self.websocket_ctx = Ctx(f"starlette_ws_{random_string()}")

    async def send(self, data: Union[Stream[bytes], bytes]) -> None:
        ws = self.websocket_ctx.get()
        if ws is None:
            raise RuntimeError("Websocket connection not prepared")
        if isinstance(data, Stream):
            data = await data.unwrap()
        await ws.send_bytes(data)

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

    async def ping(self) -> None:
        raise NotImplementedError

    async def pong(self) -> None:
        raise NotImplementedError


class StarletteServer(HttpServer, WebsocketServer, ASGIHandlerProvider):
    starlette: Starlette

    def __init__(self, service: "StarletteService", starlette: Starlette):
        self.service = service
        self.starlette = starlette

        super().__init__()

    def get_asgi_handler(self):
        return self.starlette

    def http_listen(
        self,
        path: str = "/",
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

    def websocket_listen(self, path: str = "/"):
        def wrapper(callback: Callable[[StarletteWebsocketServerConnection], Any]):
            async def _wrapper(websocket: WebSocket):
                ws = StarletteWebsocketServerConnection()
                with ws.websocket_ctx.use(websocket):
                    await callback(ws)

            self.starlette.add_websocket_route(path, _wrapper)

        return wrapper


class StarletteService(Service):
    supported_interface_types = ({StarletteServer, HttpServer, WebsocketServer, ASGIHandlerProvider}, {})

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

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent("http.universal_server", set())
