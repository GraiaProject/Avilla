from __future__ import annotations

import asyncio
from functools import partial, reduce
from pathlib import Path
from typing import Optional, Union
from weakref import WeakValueDictionary

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from starlette.websockets import WebSocket, WebSocketState
from yarl import URL

from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.asgi import ASGIHandlerProvider
from graia.amnesia.transport.common.http import AbstractServerRequestIO
from graia.amnesia.transport.common.http import HttpEndpoint as HttpEndpoint
from graia.amnesia.transport.common.http.extra import HttpRequest
from graia.amnesia.transport.common.server import AbstractRouter, AbstractServerService
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
from graia.amnesia.transport.common.websocket.operator import (
    WSConnectionAccept as WebsocketAccept,
)
from graia.amnesia.transport.common.websocket.operator import (
    WSConnectionClose as WebsocketClose,
)
from graia.amnesia.transport.exceptions import ConnectionClosed
from graia.amnesia.utilles import random_id


class StarletteServer(ASGIHandlerProvider):
    starlette: Starlette
    service: StarletteService

    def __init__(self, service: StarletteService, starlette: Starlette):
        self.service = service
        self.starlette = starlette

        super().__init__()

    def get_asgi_handler(self):
        return self.starlette


class StarletteRequestIO(AbstractServerRequestIO):
    request: Request

    def __init__(self, request: Request) -> None:
        self.request = request

    async def read(self) -> bytes:
        return await self.request.body()

    async def extra(self, signature):
        if signature is HttpRequest:
            url = self.request.url
            return HttpRequest(
                dict(self.request.headers),
                self.request.cookies,
                dict(self.request.query_params),
                URL.build(
                    scheme=url.scheme,
                    user=url.username,
                    password=url.password,
                    host=url.hostname or "",
                    port=url.port,
                    path=url.path,
                    query=url.query,
                    fragment=url.fragment,
                ),
                self.request.url.hostname or self.request.headers.get("Host", ""),
                self.request.method,
                self.request.client.host if self.request.client else ".0.0.0",
                self.request.client.port if self.request.client else 0,
            )


class StarletteWebsocketIO(AbstractWebsocketIO):
    websocket: WebSocket
    ready: asyncio.Event

    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.ready = asyncio.Event()

    async def receive(self) -> Union[str, bytes]:
        received = await self.websocket.receive()
        if "text" in received:
            return received["text"]
        elif "bytes" in received:
            return received["bytes"]
        else:
            if self.websocket.client_state == WebSocketState.DISCONNECTED:
                raise ConnectionClosed("Connection closed")
            raise TypeError(f"Unknown type of received message {received}")

    async def send(self, data: Union[bytes, str]):
        if isinstance(data, str):
            await self.websocket.send_text(data)
        elif isinstance(data, bytes):
            await self.websocket.send_bytes(data)
        else:
            raise TypeError("Unknown type of data to send")

    async def extra(self, signature):
        if signature is HttpRequest:
            url = self.websocket.url
            return HttpRequest(
                dict(self.websocket.headers),
                self.websocket.cookies,
                dict(self.websocket.query_params),
                URL.build(
                    scheme=url.scheme,
                    user=url.username,
                    password=url.password,
                    host=url.hostname or "",
                    port=url.port,
                    path=url.path,
                    query=url.query,
                    fragment=url.fragment,
                ),
                self.websocket.url.hostname or self.websocket.headers.get("Host", ""),
                "WS",
                self.websocket.client.host if self.websocket.client else "0.0.0.0",
                self.websocket.client.port if self.websocket.client else 0,
            )
        elif signature is WebsocketAccept:
            await self.websocket.accept()
        elif signature is WebsocketClose:
            await self.websocket.close()

    async def headers(self):
        return dict(self.websocket.headers)

    async def cookies(self):
        return self.websocket.cookies

    async def close(self):
        await self.websocket.close()

    async def wait_for_ready(self):
        return await self.ready.wait()

    async def accept(self):
        self.ready.set()
        return await super().accept()

    @property
    def closed(self):
        return self.websocket.application_state == WebSocketState.DISCONNECTED


class StarletteRouter(AbstractRouter["StarletteService", str, "StarletteRequestIO | StarletteWebsocketIO"]):
    def __init__(self, starlette: Starlette):
        self.starlette = starlette
        self.connections = WeakValueDictionary()
        self.transports = []

    async def handle_http_request(self, handler, request: Request):
        io = StarletteRequestIO(request)
        conn_id = random_id()
        self.connections[conn_id] = io
        try:
            response = await handler(io)
        finally:
            del self.connections[conn_id]

        if not isinstance(response, tuple):
            response_body = response
            response_desc = {}
        else:
            response_body = response[0]
            response_desc = reduce(lambda x, y: dict(x, **y), response[1:], {})

        if isinstance(response_body, (str, bytes)):
            starlette_resp = PlainTextResponse(
                response_body, status_code=response_desc.get("status", 200), headers=response_desc.get("headers", {})
            )
        elif isinstance(response_body, (dict, list)):
            starlette_resp = JSONResponse(
                response_body, status_code=response_desc.get("status", 200), headers=response_desc.get("headers", {})
            )
        elif isinstance(response_body, Path):
            starlette_resp = FileResponse(
                response_body, status_code=response_desc.get("status", 200), headers=response_desc.get("headers", {})
            )
        elif isinstance(response_body, Response):
            starlette_resp = response_body
        else:
            raise ValueError(f"unsupported response type {type(response_body)}")

        if "cookies" in response_desc:
            expire = response_desc.get("cookie_expires")
            for key, value in response_desc["cookies"].items():
                starlette_resp.set_cookie(key, value, expire)  # type: ignore

        return starlette_resp

    async def handle_websocket_request(self, ws: WebSocket):
        io = StarletteWebsocketIO(ws)
        conn_id = random_id()
        self.connections[conn_id] = io
        await self.trigger_callbacks(WebsocketConnectEvent, io)
        if io.closed:
            return
        io.ready.set()
        try:
            async for message in io.packets():
                await self.trigger_callbacks(WebsocketReceivedEvent, io, message)
        except ConnectionClosed:
            await self.trigger_callbacks(WebsocketCloseEvent, io)

    def use(self, transport: Transport):
        self.transports.append(transport)

        for signature, handler in transport.iter_handlers():
            if isinstance(signature, HttpEndpoint):
                self.starlette.add_route(
                    signature.path, partial(self.handle_http_request, handler), methods=signature.methods
                )

        for signature in transport.declares:
            if isinstance(signature, WebsocketEndpoint):
                self.starlette.add_websocket_route(signature.path, self.handle_websocket_request)


class StarletteService(AbstractServerService):
    id = "http.server/starlette"
    supported_interface_types = (
        {StarletteRouter, StarletteServer},
        {
            AbstractRouter: 5,  # NOTE: maybe we should sync `AbstractRouter` value with `ASGIHandlerProvider`...
            ASGIHandlerProvider: 5,
        },
    )
    starlette: Starlette

    def __init__(self, starlette: Optional[Starlette] = None) -> None:
        self.starlette = starlette or Starlette()
        super().__init__()

    def get_interface(self, interface_type):
        if issubclass(interface_type, (ASGIHandlerProvider, StarletteServer)):
            return StarletteServer(self, self.starlette)
        elif issubclass(interface_type, (AbstractRouter, StarletteRouter)):
            return StarletteRouter(self.starlette)
        raise ValueError(f"unsupported interface type {interface_type}")

    @property
    def stages(self):
        return set()

    @property
    def required(self):
        return set()

    async def launch(self, _):
        pass
