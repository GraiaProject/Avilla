import asyncio
from contextlib import ExitStack, asynccontextmanager
from typing import AsyncGenerator, Callable, List, Type, Union

from graia.broadcast.utilles import Ctx
from loguru import logger
from pydantic.main import BaseModel
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from avilla.core import LaunchComponent, Service
from avilla.core.selectors import entity as entity_selector
from avilla.core.service.common.http import (
    HTTP_METHODS,
    ASGIHandlerProvider,
    HttpServer,
    WebsocketServer,
)
from avilla.core.service.session import BehaviourSession
from avilla.core.stream import Stream


class StarletteServer(HttpServer, WebsocketServer, ASGIHandlerProvider):
    starlette: Starlette

    def __init__(self, service: "StarletteService", starlette: Starlette):
        self.service = service
        self.starlette = starlette

        super().__init__()

    def get_asgi_handler(self):
        return self.starlette

    async def http_listen(
        self,
        path: str = "/",
        methods: List[HTTP_METHODS] = None,
    ):
        pass # TODO

    async def websocket_listen(self, path: str = "/")
        pass # TODO


class StarletteService(Service):
    supported_interface_types = {StarletteServer, HttpServer, WebsocketServer, ASGIHandlerProvider}

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
