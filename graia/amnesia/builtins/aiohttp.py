from __future__ import annotations

import asyncio
from collections.abc import Callable
from contextlib import suppress
from functools import partial, reduce
from io import IOBase
from pathlib import Path
from typing import Any, Awaitable, Generic, TypeVar, cast, overload
from weakref import WeakValueDictionary

from aiohttp import (
    ClientConnectionError,
    ClientResponse,
    ClientSession,
    ClientTimeout,
    ClientWebSocketResponse,
    WSMsgType,
    web,
)
from launart.manager import Launart
from launart.utilles import wait_fut
from loguru import logger
from typing_extensions import ParamSpec, Self

from graia.amnesia.json import Json, TJson
from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.client import (
    AbstractClientInterface,
    AbstractClientService,
)
from graia.amnesia.transport.common.http import AbstractServerRequestIO
from graia.amnesia.transport.common.http import HttpEndpoint as HttpEndpoint
from graia.amnesia.transport.common.http.extra import HttpRequest, HttpResponse
from graia.amnesia.transport.common.http.io import AbstractClientRequestIO
from graia.amnesia.transport.common.server import AbstractRouter, AbstractServerService
from graia.amnesia.transport.common.status import ConnectionStatus
from graia.amnesia.transport.common.websocket import AbstractWebsocketIO
from graia.amnesia.transport.common.websocket import (
    WebsocketEndpoint as WebsocketEndpoint,
)
from graia.amnesia.transport.common.websocket.event import (
    WebsocketCloseEvent as WebsocketCloseEvent,
)
from graia.amnesia.transport.common.websocket.event import (
    WebsocketConnectEvent as WebsocketConnectEvent,
)
from graia.amnesia.transport.common.websocket.event import (
    WebsocketReceivedEvent as WebsocketReceivedEvent,
)
from graia.amnesia.transport.common.websocket.event import (
    WebsocketReconnect as WebsocketReconnect,
)
from graia.amnesia.transport.common.websocket.io import AbstractWebsocketIO
from graia.amnesia.transport.common.websocket.operator import (
    WSConnectionAccept as WebsocketAccept,
)
from graia.amnesia.transport.common.websocket.operator import (
    WSConnectionClose as WebsocketClose,
)
from graia.amnesia.transport.exceptions import ConnectionClosed
from graia.amnesia.transport.rider import TransportRider
from graia.amnesia.utilles import random_id


class AiohttpClientRequestIO(AbstractClientRequestIO):
    rider: AiohttpClientConnectionRider[ClientResponse]
    response: ClientResponse

    def __init__(self, rider: AiohttpClientConnectionRider) -> None:
        assert rider.response
        self.rider = rider
        self.response = rider.response

    async def read(self) -> bytes:
        data = await self.response.read()
        if self.rider.status.connected:
            self.close()
        return data

    async def extra(self, signature):
        if signature is HttpResponse:
            return HttpResponse(
                self.response.status,
                dict(self.response.headers.items()),
                {k: str(v) for k, v in self.response.cookies.items()},
                self.response.url,
            )

    def close(self):
        self.rider.status.connected = False
        self.response.close()


class AiohttpClientWebsocketIO(AbstractWebsocketIO):
    rider: AiohttpClientConnectionRider[ClientWebSocketResponse]
    connection: ClientWebSocketResponse

    def __init__(self, rider: AiohttpClientConnectionRider) -> None:
        assert rider.response
        self.rider = rider
        self.connection = rider.response

    async def cookies(self) -> dict[str, str]:
        return {k: v.value for k, v in self.connection._response.cookies.items()}

    async def extra(self, signature):
        if signature is WebsocketClose:
            if not self.connection.closed:
                await self.connection.close()
        elif signature is HttpResponse:
            return HttpResponse(
                self.connection._response.status,
                dict(self.connection._response.request_info.headers.items()),
                {k: v.value for k, v in self.connection._response.cookies.items()},
                self.connection._response.request_info.url,
            )

    async def receive(self) -> bytes | str:
        msg = await self.connection.receive()
        if msg.type in {WSMsgType.TEXT, WSMsgType.BINARY}:
            return msg.data
        # 错误处理
        if msg.type in {WSMsgType.CLOSE, WSMsgType.CLOSED}:
            raise ConnectionClosed("websocket closed")
        elif msg.type == WSMsgType.ERROR:
            raise msg.data
        else:
            raise TypeError(f"unexpected websocket message type: {msg.type}")

    async def send(self, data: "str | bytes | Any"):
        try:
            if isinstance(data, str):
                await self.connection.send_str(data)
            elif isinstance(data, bytes):
                await self.connection.send_bytes(data)
            else:
                await self.connection.send_json(data)
        except ConnectionError as e:
            raise ConnectionClosed(e.__class__.__qualname__, *e.args) from None

    @property
    def closed(self):
        return self.connection.closed

    async def wait_for_ready(self):
        if self.closed:
            raise ConnectionClosed("websocket closed")
        # TODO

    async def close(self):
        self.rider.status.connected = False
        await self.extra(WebsocketClose)


T = TypeVar("T", ClientResponse, ClientWebSocketResponse)

P = ParamSpec("P")


class AiohttpClientConnectionRider(TransportRider[str, T], Generic[T]):
    def __init__(
        self,
        interface: AiohttpClientInterface,
        conn_func: Callable[..., Awaitable[T]],
        call_param: dict[str, Any],
    ) -> None:
        self.transports: list[Transport] = []
        self.connections = {}
        self.response: T | None = None
        self.conn_func = conn_func
        self.call_param = call_param
        self.status = ConnectionStatus()
        self.auto_receive: bool = False
        self.task = None
        self.interface = interface

    async def _start_conn(self) -> Self:
        if not self.status.available:
            self.response = await self.conn_func(**self.call_param)
            self.status.connected = True
            self.status.succeed = True
        return self

    def __await__(self):
        return self._start_conn().__await__()

    @overload
    def io(self: "AiohttpClientConnectionRider[ClientResponse]") -> AiohttpClientRequestIO:
        ...

    @overload
    def io(self: "AiohttpClientConnectionRider[ClientWebSocketResponse]") -> AiohttpClientWebsocketIO:
        ...

    def io(self, id=None) -> ...:
        if id:
            raise TypeError("this rider has just one connection")
        if self.auto_receive:
            raise TypeError("this rider has been taken over by auto receive, use .use(transport) instead.")
        if not self.status.connected:
            raise RuntimeError("the connection is not ready, please await the instance to ensure connection")
        assert self.response
        if isinstance(self.response, ClientWebSocketResponse):
            return AiohttpClientWebsocketIO(self)
        elif isinstance(self.response, ClientResponse):
            return AiohttpClientRequestIO(self)
        else:
            raise TypeError("this response is not a ClientResponse or ClientWebSocketResponse")

    async def connection_manage(self):
        __original_transports: list[Transport] = self.transports[:]

        with suppress(Exception):
            while self.transports and not Launart.current().status.exiting:
                try:
                    await self._start_conn()
                    assert isinstance(
                        self.response, ClientWebSocketResponse
                    ), f"{self.response} is not a ClientWebSocketResponse"
                    io = AiohttpClientWebsocketIO(self)
                    await self.trigger_callbacks(WebsocketConnectEvent, io)
                    with suppress(ConnectionClosed):
                        async for data in io.packets():
                            await self.trigger_callbacks(WebsocketReceivedEvent, io, data)
                    await self.trigger_callbacks(WebsocketCloseEvent, io)
                    await io.close()
                except ClientConnectionError as e:
                    logger.warning(repr(e))
                except Exception as e:
                    logger.exception(e)
                # scan transports
                if Launart.current().status.exiting:
                    continue
                continuing_transports: list[Transport] = self.transports[:]
                self.transports = []
                reconnect_handle_tasks = []
                for t in continuing_transports:
                    if t.has_handler(WebsocketReconnect):
                        handler = t.get_handler(WebsocketReconnect)
                        tsk = asyncio.create_task(handler(self.status))
                        if not tsk.cancelled():
                            tsk.add_done_callback(
                                lambda tsk: self.transports.append(t) if tsk.result() is True else None
                            )
                            reconnect_handle_tasks.append(tsk)
                await wait_fut(reconnect_handle_tasks)
        self.transports = __original_transports

    def use(self, transport: Transport):
        self.auto_receive = True
        self.transports.append(transport)
        if not self.task:
            self.task = asyncio.create_task(self.connection_manage())
        return self.task


class AiohttpClientInterface(AbstractClientInterface["AiohttpClientService"]):
    def __init__(self, service: AiohttpClientService) -> None:
        self.service = service

    def request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        data: Any = None,
        headers: dict | None = None,
        cookies: dict | None = None,
        timeout: float | None = None,
        *,
        json: TJson | None = None,
        **kwargs: Any,
    ) -> AiohttpClientConnectionRider[ClientResponse]:
        if json:
            data = Json.serialize(json)
        call_param: dict[str, Any] = {
            "method": method,
            "url": url,
            "params": params,
            "data": data,
            "headers": headers,
            "cookies": cookies,
            "timeout": timeout,
            **kwargs,
        }
        return AiohttpClientConnectionRider(self, self.service.session.request, call_param)

    def websocket(self, url: str, **kwargs) -> AiohttpClientConnectionRider[ClientWebSocketResponse]:
        call_param: dict[str, Any] = {"url": url, **kwargs}
        return AiohttpClientConnectionRider(self, self.service.session.ws_connect, call_param)


class AiohttpClientService(AbstractClientService):
    id = "http.client/aiohttp"
    session: ClientSession
    supported_interface_types = {AiohttpClientInterface}, {
        AbstractClientInterface: 7
    }  # NOTE: Seems to be the fastest one...

    def __init__(self, session: ClientSession | None = None) -> None:
        self.session = cast(ClientSession, session)
        super().__init__()

    def get_interface(self, _):
        return AiohttpClientInterface(self)

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @property
    def required(self):
        return set()

    async def launch(self, mgr: Launart):
        async with self.stage("preparing"):
            if not self.session:
                self.session = ClientSession(timeout=ClientTimeout(total=None))
        async with self.stage("cleanup"):
            await self.session.close()


class AiohttpServerRequestIO(AbstractServerRequestIO):
    request: web.Request

    def __init__(self, request: web.Request) -> None:
        self.request = request

    async def read(self) -> bytes:
        return await self.request.content.read()

    async def extra(self, signature):
        if signature is HttpRequest:
            return HttpRequest(
                dict(self.request.headers.items()),
                dict(self.request.cookies),
                dict(self.request.query.items()),
                self.request.url,
                self.request.host,
                self.request.method,
                self.request.remote or ".0.0.0",
                0,
            )


class AiohttpServerWebsocketIO(AbstractWebsocketIO):
    websocket: web.WebSocketResponse
    request: web.Request
    ready: asyncio.Event

    def __init__(self, request: web.Request) -> None:
        self.websocket = web.WebSocketResponse(autoping=True)
        self.request = request
        self.ready = asyncio.Event()

    async def receive(self) -> bytes | str:
        try:
            received = await self.websocket.receive()
        except asyncio.CancelledError as e:
            raise ConnectionClosed("Cancelled") from e
        if received.type in (web.WSMsgType.BINARY, web.WSMsgType.TEXT):
            return received.data
        elif received.type in (web.WSMsgType.CLOSE, web.WSMsgType.CLOSING, web.WSMsgType.CLOSED):
            self.ready.clear()
            raise ConnectionClosed("Connection closed")
        elif received.type is web.WSMsgType.ERROR:
            exc = self.websocket.exception()
            raise ConnectionClosed("Websocket Error") from exc
        raise TypeError(f"Unknown type of received message {received}")

    async def send(self, data: Any):
        if isinstance(data, str):
            await self.websocket.send_str(data)
        elif isinstance(data, bytes):
            await self.websocket.send_bytes(data)
        else:
            await self.websocket.send_json(data)

    async def extra(self, signature):
        if signature is HttpRequest:
            return HttpRequest(
                dict(self.request.headers.items()),
                dict(self.request.cookies),
                dict(self.request.query.items()),
                self.request.url,
                self.request.host,
                self.request.method,
                self.request.remote or ".0.0.0",
                0,
            )
        elif signature is WebsocketAccept:
            await self.websocket.prepare(self.request)
            self.ready.set()
        elif signature is WebsocketClose:
            await self.websocket.close()

    async def wait_for_ready(self):
        return await self.ready.wait()

    async def accept(self):
        return await super().accept()

    async def headers(self) -> dict[str, str]:
        return dict(self.websocket.headers.items())

    async def cookies(self) -> dict[str, str]:
        return dict(self.request.cookies)

    async def close(self):
        await self.websocket.close()

    @property
    def closed(self):
        return self.websocket.closed


class AiohttpRouter(AbstractRouter["AiohttpServerService", str, "AiohttpServerRequestIO | AiohttpServerWebsocketIO"]):
    def __init__(self, wsgi: web.Application) -> None:
        self.connections = WeakValueDictionary()
        self.transports = []
        self.wsgi = wsgi

    async def handle_http_request(self, handler: Callable[[AiohttpServerRequestIO], Any], request: web.Request):
        req_io = AiohttpServerRequestIO(request)
        conn_id = random_id()
        self.connections[conn_id] = req_io
        try:
            handler_resp = await handler(req_io)
        finally:
            del self.connections[conn_id]
        if not isinstance(handler_resp, tuple):
            body = handler_resp
            resp_info = {}
        else:
            body = handler_resp[0]
            resp_info = reduce(lambda x, y: dict(x, **y), handler_resp[1:], {})
        status: int = resp_info.get("status", 200)
        if isinstance(body, (str, bytes, IOBase)):
            response = web.Response(body=body, status=status)
        elif isinstance(body, (dict, list)):
            response = web.json_response(body, status=status, headers=resp_info.get("headers"))
        elif isinstance(body, Path):
            response = web.Response(body=body.open("rb"), status=status)
        elif isinstance(body, web.Response):
            response = body
        else:
            raise ValueError(f"unsupported response type {type(body)}")

        if "cookies" in resp_info:
            expire = resp_info.get("cookie_expires")
            for key, value in resp_info["cookies"].items():
                response.set_cookie(key, value, expires=expire)

        return response

    async def handle_websocket_request(self, request: web.Request) -> web.WebSocketResponse:
        websocket_io = AiohttpServerWebsocketIO(request)
        conn_id = random_id()
        self.connections[conn_id] = websocket_io
        await self.trigger_callbacks(WebsocketConnectEvent, websocket_io)
        if websocket_io.closed:
            return websocket_io.websocket
        with suppress(ConnectionClosed):
            async for message in websocket_io.packets():
                await self.trigger_callbacks(WebsocketReceivedEvent, websocket_io, message)
        await self.trigger_callbacks(WebsocketCloseEvent, websocket_io)
        await websocket_io.close()
        return websocket_io.websocket

    def use(self, transport: Transport):
        self.transports.append(transport)
        for signature, handler in transport.iter_handlers():
            if isinstance(signature, HttpEndpoint):
                for method in signature.methods:
                    self.wsgi.router.add_route(method, signature.path, partial(self.handle_http_request, handler))

        for signature in transport.declares:
            if isinstance(signature, WebsocketEndpoint):
                self.wsgi.router.add_route("GET", signature.path, self.handle_websocket_request)


class AiohttpServerService(AbstractServerService):
    id = "http.server/aiohttp"
    wsgi_handler: web.Application
    supported_interface_types = {AiohttpRouter}, {
        AbstractRouter: 4,  # NOTE: Seems slower than Starlette...
    }

    def __init__(self, host: str = "127.0.0.1", port: int = 8000, wsgi_handler: web.Application | None = None) -> None:
        self.wsgi_handler = wsgi_handler or web.Application()
        self.wsgi_handler.router.freeze = lambda: None  # monkey patch
        self.routers: list[AiohttpRouter] = []
        self.host = host
        self.port = port
        super().__init__()

    def get_interface(self, _):
        router = AiohttpRouter(self.wsgi_handler)
        self.routers.append(router)
        return router

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    @property
    def required(self):
        return set()

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            logger.info(f"starting server on {self.host}:{self.port}")
            runner = web.AppRunner(self.wsgi_handler)
            await runner.setup()
            site = web.TCPSite(runner, self.host, self.port)
        async with self.stage("blocking"):
            await site.start()
        async with self.stage("cleanup"):
            await self.wsgi_handler.shutdown()
            await self.wsgi_handler.cleanup()
