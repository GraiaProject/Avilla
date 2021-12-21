import asyncio
from contextlib import asynccontextmanager
from typing import Type, AsyncGenerator, List, Union, Callable

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket
from uvicorn import Server, Config

from avilla.core import Service, LaunchComponent
from avilla.core.selectors import entity as entity_selector
from avilla.core.service import TInterface, BehaviourDescription
from avilla.core.service.common.activities import disconnect
from avilla.core.service.common.behaviours import DataReceived, PostConnected, PostDisconnected
from avilla.core.service.common.http import HttpServer, WebsocketServer, HTTP_METHODS
from avilla.core.service.session import BehaviourSession
from avilla.core.stream import Stream


class StarletteServer(HttpServer, WebsocketServer):
    starlette: Starlette
    server: Server

    def __init__(self, service: "StarletteService", starlette: Starlette, server: Server):
        self.service = service
        self.starlette = starlette
        self.server = server

        super().__init__()

    @asynccontextmanager
    async def http_listen(
        self,
        path: str = "/",
        methods: List[HTTP_METHODS] = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        cbs = {
            DataReceived: [],
            PostConnected: [],  # TODO:对于http listen，这意味着单次连接的开始与终止，还是server生命的开始与终止？（以下为后者实现）
            PostDisconnected: [],
        }

        def cb_handler(
            behaviour: Union[Type[BehaviourDescription], BehaviourDescription], callback: Callable
        ) -> None:
            if behaviour is DataReceived or isinstance(behaviour, DataReceived):
                cbs[DataReceived].append(callback)
            elif behaviour is PostConnected or isinstance(behaviour, PostConnected):
                cbs[PostConnected].append(callback)
            elif behaviour is PostDisconnected or isinstance(behaviour, PostDisconnected):
                cbs[PostDisconnected].append(callback)

        prepared_signal = asyncio.Event()
        behaviour_session = BehaviourSession(self.service, self, {}, prepared_signal)

        async def startup() -> None:
            await prepared_signal.wait()
            behaviour_session.update_activity_handlers(
                {
                    # send_netmsg: None, #TODO:是否有必要使用response调用平台功能？（实现可能有一定困难）
                    disconnect: lambda _: self.server.shutdown(),
                }
            )
            behaviour_session.submit_behaviour_expansion(cb_handler)
            current_session_stats = {}

            @self.starlette.route(path, methods=methods or ["POST"])
            async def http_route(request: Request):
                await asyncio.gather(
                    *[
                        cb(
                            self,
                            behaviour_session,
                            current_session_stats,
                            Stream(await request.body()),
                        )
                        for cb in cbs[DataReceived]
                    ]
                )
                return Response()

            await asyncio.gather(
                *[cb(self, behaviour_session, current_session_stats) for cb in cbs[PostConnected]]
            )

            await self.server.main_loop()

            await asyncio.gather(
                *[cb(self, behaviour_session, current_session_stats) for cb in cbs[PostDisconnected]]
            )

        asyncio.create_task(startup())
        yield behaviour_session

    @asynccontextmanager
    async def websocket_listen(
        self,
        path: str = "/"
    ) -> "AsyncGenerator[BehaviourSession, None]":  # TODO
        @self.starlette.websocket_route(path)
        async def websocket_route(websocket: WebSocket):
            pass

        yield


class StarletteService(Service):
    supported_interface_types = {StarletteServer, HttpServer, WebsocketServer}
    supported_description_types = {DataReceived, PostConnected, PostDisconnected}

    starlette: Starlette
    server: Server

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        starlette: Starlette = None
    ) -> None:
        self.starlette = starlette or Starlette()
        self.server = Server(Config(self.starlette, host, port))
        super().__init__()

    def get_interface(self, interface_type: Type[TInterface]) -> TInterface:
        if issubclass(interface_type, (HttpServer, WebsocketServer)):
            return StarletteServer(self, self.starlette, self.server)
        raise ValueError(f"unsupported interface type {interface_type}")

    def get_status(self, entity: entity_selector = None):
        if entity is None:
            return self.status
        if entity not in self.status:
            raise KeyError(f"{entity} not in status")
        return self.status[entity]

    async def launch_mainline(self):
        ...

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            "http.universal_server",
            set(),
            self.launch_mainline,
            self.server.serve,
            self.server.shutdown,
        )
