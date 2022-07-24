import asyncio
from collections.abc import Coroutine

from avilla.core.account import AbstractAccount
from avilla.core.relationship import Relationship
from avilla.core.utilles.selector import Selector

from .connection import (
    OneBot11HttpClientConnection,
    OneBot11HttpServerConnection,
    OneBot11WebsocketClientConnection,
    OneBot11WebsocketServerConnection,
)
from .protocol import OneBot11Protocol


class OneBot11Account(AbstractAccount):
    protocol: OneBot11Protocol

    http_client: OneBot11HttpClientConnection | None = None
    http_server: OneBot11HttpServerConnection | None = None
    websocket_client: OneBot11WebsocketClientConnection | None = None
    websocket_server: OneBot11WebsocketServerConnection | None = None

    async def call(self, action: str, params: dict):
        coros: set[Coroutine] = set()
        for connection in filter(None, (self.websocket_client, self.websocket_server, self.http_client)):
            if connection.status.available:
                return await connection.call(action, params)
            else:
                coros.add(connection.status.wait_for_available())

        await asyncio.wait(map(asyncio.ensure_future, coros), return_when=asyncio.FIRST_COMPLETED)

        for connection in filter(None, (self.websocket_client, self.websocket_server, self.http_client)):
            if connection.status.available:
                return await connection.call(action, params)

        raise RuntimeError("No available connection")

    async def get_relationship(self, target: Selector) -> Relationship:
        return await super().get_relationship(target)

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
