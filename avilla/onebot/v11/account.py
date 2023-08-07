from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from launart.utilles import any_completed

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector
from avilla.onebot.v11.net.ws_server import OneBot11WsServerConnection
from avilla.standard.core.account import AccountAvailable, AccountUnavailable

if TYPE_CHECKING:
    from .net.ws_client import OneBot11WsClientNetworking
    from .protocol import OneBot11Protocol


class OneBot11Account(BaseAccount):
    protocol: OneBot11Protocol
    status: AccountStatus

    # http_client: OneBot11HttpClientConnection | None = None
    # http_server: OneBot11HttpServerConnection | None = None
    websocket_client: OneBot11WsClientNetworking | None = None
    websocket_server: OneBot11WsServerConnection | None = None

    def __init__(self, route: Selector, protocol: OneBot11Protocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()

    @contextmanager
    def _status_update(self):
        prev = self.available
        yield
        if prev != (curr := self.available):
            avilla = self.protocol.avilla
            avilla.broadcast.postEvent((AccountAvailable if curr else AccountUnavailable)(avilla, self))

    async def call(self, endpoint: str, params: dict):
        coros = set()
        for connection in (self.websocket_client, self.websocket_server):
            if connection is None:
                continue
            if connection.alive:
                return await connection.call(endpoint, params)
            coros.add(connection.wait_for_available())

        if coros:
            await any_completed(*coros)
            for connection in (self.websocket_client, self.websocket_server):
                if connection is None:
                    continue
                if connection.alive:
                    return await connection.call(endpoint, params)

        raise RuntimeError("No available connection")

    @property
    def available(self) -> bool:
        return self.status.enabled
