from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from avilla.core.account import BaseAccount
from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.standard.core.account import AccountAvailable, AccountUnavailable
from launart.utilles import any_completed

from .connection_old import (
    OneBot11HttpClientConnection,
    OneBot11HttpServerConnection,
    OneBot11WebsocketClientConnection,
    OneBot11WebsocketServerConnection,
)

if TYPE_CHECKING:
    from .protocol import OneBot11Protocol


class OneBot11Account(BaseAccount):
    protocol: OneBot11Protocol

    http_client: OneBot11HttpClientConnection | None = None
    http_server: OneBot11HttpServerConnection | None = None
    websocket_client: OneBot11WebsocketClientConnection | None = None
    websocket_server: OneBot11WebsocketServerConnection | None = None

    def __init__(self, route: Selector, protocol: OneBot11Protocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol

    @contextmanager
    def _status_update(self):
        prev = self.available
        yield
        if prev != (curr := self.available):
            avilla = self.protocol.avilla
            avilla.broadcast.postEvent((AccountAvailable if curr else AccountUnavailable)(avilla, self))

    async def get_context(self, target: Selector, *, via: Selector | None = None) -> Context:
        ...

    async def call(self, endpoint: str, params: dict):
        coros = set()
        for connection in filter(None, (self.websocket_client, self.websocket_server, self.http_client)):
            if connection.status.available:
                return await connection.call(endpoint, params)
            coros.add(connection.status.wait_for_available())

        if coros:
            await any_completed(*coros)
            for connection in filter(None, (self.websocket_client, self.websocket_server, self.http_client)):
                if connection.status.available:
                    return await connection.call(endpoint, params)

        raise RuntimeError("No available connection")

    @property
    def available(self) -> bool:
        return bool(
            (self.websocket_client and self.websocket_client.status.available)  # WS Client
            or (self.websocket_server and self.websocket_server.status.available)  # WS Server
            or (
                self.http_client
                and self.http_client.status.available
                and self.http_server
                and self.http_server.status.available
            )  # HTTP Client & Server
        )
