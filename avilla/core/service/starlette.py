import asyncio
from contextlib import ExitStack, asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, Callable, List, Type, Union

from graia.broadcast.utilles import Ctx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from avilla.core import LaunchComponent, Service
from avilla.core.selectors import entity as entity_selector
from avilla.core.service import BehaviourDescription
from avilla.core.service.common.activities import (
    accept,
    disconnect,
    del_cookie,
    get_cookie,
    set_cookie,
    get_header,
    set_header,
    set_status,
    respond,
    send,
)
from avilla.core.service.common.behaviours import (
    DataReceived,
    PostConnected,
    PostDisconnected,
    PreConnected,
)
from avilla.core.service.common.http import (
    HTTP_METHODS,
    ASGIHandlerProvider,
    HttpServer,
    WebsocketServer,
)
from avilla.core.service.session import BehaviourSession
from avilla.core.stream import Stream

if TYPE_CHECKING:
    from avilla.core import Avilla


class StarletteServer(HttpServer, WebsocketServer, ASGIHandlerProvider):
    starlette: Starlette

    def __init__(self, service: "StarletteService", starlette: Starlette):
        self.service = service
        self.starlette = starlette

        super().__init__()

    def get_asgi_handler(self):
        return self.starlette

    @asynccontextmanager
    async def http_listen(
        self,
        path: str = "/",
        methods: List[HTTP_METHODS] = None,
    ) -> "AsyncGenerator[BehaviourSession, None]":
        cbs = {DataReceived: []}

        def cb_handler(
            behaviour: Union[Type[BehaviourDescription], BehaviourDescription], callback: Callable
        ) -> None:
            if behaviour is DataReceived or isinstance(behaviour, DataReceived):
                cbs[DataReceived].append(callback)

        prepared_signal = asyncio.Event()
        session = BehaviourSession(self.service, self, {}, prepared_signal)

        async def add_route() -> None:
            await prepared_signal.wait()
            session.submit_behaviour_expansion(cb_handler)

            @self.starlette.route(path, methods=methods or ["POST"])
            async def http_route(request: Request):
                fut = asyncio.get_running_loop().create_future()
                modifies_on_cookie = []
                modifies_on_header = []
                httpstatus = None

                def cb_act_respond(activity: Union[respond, None]) -> None:
                    if activity is None:
                        raise ValueError("respond as a activity cannot be None")
                    fut.set_result(activity.data)

                def cb_act_httpcookie_get(activity: Union[get_cookie, None]) -> Union[str, None]:
                    if activity is None:
                        raise ValueError("httpcookie_get as a activity cannot be None")
                    return request.cookies.get(activity.key)

                def cb_act_httpcookie_set(activity: Union[set_cookie, None]) -> None:
                    if activity is None:
                        raise ValueError("httpcookie_set as a activity cannot be None")
                    modifies_on_cookie.append(("SET", activity.key, activity.value))

                def cb_act_httpcookie_delete(activity: Union[del_cookie, None]) -> None:
                    if activity is None:
                        raise ValueError("httpcookie_delete as a activity cannot be None")
                    modifies_on_cookie.append(("DELETE", activity.key, None))

                def cb_act_httpheader_get(activity: Union[get_header, None]) -> Union[str, None]:
                    if activity is None:
                        raise ValueError("httpheader_get as a activity cannot be None")
                    return request.headers.get(activity.key)

                def cb_act_httpheader_set(activity: Union[set_header, None]) -> None:
                    if activity is None:
                        raise ValueError("httpheader_set as a activity cannot be None")
                    modifies_on_header.append((activity.key, activity.value))

                def cb_act_httpstatus_set(activity: Union[set_status, None]) -> None:
                    if activity is None:
                        raise ValueError("httpstatus_set as a activity cannot be None")
                    nonlocal httpstatus
                    httpstatus = activity.status

                session.update_activity_handlers(
                    {
                        respond: cb_act_respond,
                        get_cookie: cb_act_httpcookie_get,
                        set_cookie: cb_act_httpcookie_set,
                        del_cookie: cb_act_httpcookie_delete,
                        get_header: cb_act_httpheader_get,
                        set_header: cb_act_httpheader_set,
                        set_status: cb_act_httpstatus_set,
                    }  # type: ignore
                )
                await asyncio.gather(
                    *[
                        cb(
                            self,
                            session,
                            {},
                            Stream(await request.body()),
                        )
                        for cb in cbs[DataReceived]
                    ]
                )
                response = await fut
                if isinstance(response, Response):
                    for mod, key, value in modifies_on_cookie:
                        if mod == "SET":
                            response.set_cookie(key, value)
                        elif mod == "DELETE":
                            response.delete_cookie(key)
                    for k, v in modifies_on_header:
                        response.headers[k] = v
                    if httpstatus is not None:
                        response.status_code = httpstatus
                return response

        asyncio.create_task(add_route())
        yield session

    @asynccontextmanager
    async def websocket_listen(self, path: str = "/") -> "AsyncGenerator[BehaviourSession, None]":
        cbs = {DataReceived: [], PreConnected: [], PostConnected: [], PostDisconnected: []}
        ctx_ws: Ctx[WebSocket] = Ctx("ctx_ws")

        def cb_handler(
            behaviour: Union[Type[BehaviourDescription], BehaviourDescription], callback: Callable
        ) -> None:
            if behaviour is DataReceived or isinstance(behaviour, DataReceived):
                cbs[DataReceived].append(callback)
            elif behaviour is PostConnected or isinstance(behaviour, PostConnected):
                cbs[PostConnected].append(callback)
            elif behaviour is PostDisconnected or isinstance(behaviour, PostDisconnected):
                cbs[PostDisconnected].append(callback)
            elif behaviour is PreConnected or isinstance(behaviour, PreConnected):
                cbs[PreConnected].append(callback)

        prepared_signal = asyncio.Event()
        behaviour_session = BehaviourSession(self.service, self, {}, prepared_signal)
        behaviour_session.submit_behaviour_expansion(cb_handler)

        async def trig_cbs(
            key: Union[Type[PreConnected], Type[PostConnected], Type[PostDisconnected], Type[DataReceived]],
            stats: dict,
            *args,
            **kwargs,
        ):
            for cb in cbs[key]:
                await cb(self, behaviour_session, stats, *args, **kwargs)

        async def add_route() -> None:
            @self.starlette.websocket_route(path)
            async def websocket_route(ws: WebSocket):
                await prepared_signal.wait()
                conn_stats = {
                    "connected": False,
                    "disconnected": False,
                }

                def cb_act_httpheader_get(activity: Union[get_header, None]) -> Union[str, None]:
                    if activity is None:
                        raise ValueError("httpheader_get as a activity cannot be None")
                    return ws.headers.get(activity.key)

                async def cb_act_accept(_) -> None:
                    conn_stats["connected"] = True
                    await ws.accept()

                async def cb_act_disconnect(_) -> None:
                    conn_stats["disconnect"] = True
                    if conn_stats["connected"]:
                        await ws.close()

                async def cb_act_send(activity: Union[send, None]) -> None:
                    if activity is None:
                        raise ValueError("send as a activity cannot be None")
                    if isinstance(activity.data, str):
                        await ws.send_text(activity.data)
                    elif isinstance(activity.data, bytes):
                        await ws.send_bytes(activity.data)
                    else:
                        raise ValueError(f"Unsupported data type {type(activity.data)}")

                behaviour_session.update_activity_handlers(
                    {
                        accept: cb_act_accept,
                        disconnect: cb_act_disconnect,
                        get_header: cb_act_httpheader_get,
                    }
                )
                with ExitStack() as stack:
                    stack.enter_context(ctx_ws.use(ws))
                    await trig_cbs(PreConnected, conn_stats)
                    if not conn_stats["connected"]:
                        return
                    behaviour_session.update_activity_handlers(
                        {  # type: ignore
                            disconnect: cb_act_disconnect,
                            send: cb_act_send,
                            get_header: cb_act_httpheader_get,
                        },
                        clean=True,
                    )
                    await trig_cbs(PostConnected, conn_stats)
                    while not conn_stats["disconnected"]:
                        try:
                            received_data = await ws.receive_bytes()
                        except WebSocketDisconnect:
                            conn_stats["disconnected"] = True
                            break
                        await trig_cbs(DataReceived, conn_stats, Stream(received_data))
                    await trig_cbs(PostDisconnected, conn_stats)

        asyncio.create_task(add_route())
        yield behaviour_session


class StarletteService(Service):
    supported_interface_types = {StarletteServer, HttpServer, WebsocketServer, ASGIHandlerProvider}
    supported_description_types = {DataReceived, PostConnected, PostDisconnected, PreConnected}

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

    async def launch_mainline(self, avilla: "Avilla"):
        ...

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            "http.universal_server",
            set(),
            self.launch_mainline,
        )
