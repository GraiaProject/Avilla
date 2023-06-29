from __future__ import annotations

import asyncio
from contextlib import contextmanager
from typing import TYPE_CHECKING

from avilla.core.account import AbstractAccount
from avilla.standard.core.application import AccountAvailable, AccountUnavailable
from avilla.core.context import Context
from avilla.core.selector import Selector
from launart.utilles import any_completed

from .connection import (
    OneBot11HttpClientConnection,
    OneBot11HttpServerConnection,
    OneBot11WebsocketClientConnection,
    OneBot11WebsocketServerConnection,
)

if TYPE_CHECKING:
    from .protocol import OneBot11Protocol


class OneBot11Account(AbstractAccount):
    protocol: OneBot11Protocol

    http_client: OneBot11HttpClientConnection | None = None
    http_server: OneBot11HttpServerConnection | None = None
    websocket_client: OneBot11WebsocketClientConnection | None = None
    websocket_server: OneBot11WebsocketServerConnection | None = None

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
            (self.websocket_client and self.websocket_client.status.available)
            or (self.websocket_server and self.websocket_server.status.available)
            or (
                self.http_client
                and self.http_client.status.available
                and self.http_server
                and self.http_server.status.available
            )
        )