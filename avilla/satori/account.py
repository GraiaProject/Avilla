from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector
from avilla.standard.core.account import AccountAvailable, AccountUnavailable

if TYPE_CHECKING:
    from .net.ws_client import SatoriWsClientNetworking
    from .protocol import SatoriProtocol


class SatoriAccount(BaseAccount):
    protocol: SatoriProtocol
    status: AccountStatus
    client: SatoriWsClientNetworking | None = None

    def __init__(self, route: Selector, protocol: SatoriProtocol):
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
        if self.client is None:
            raise RuntimeError("No available connection")
        if self.client.alive:
            return await self.client.call(endpoint, params)
        await self.client.wait_for_available()
        if self.client.alive:
            return await self.client.call(endpoint, params)
        raise RuntimeError("No available connection")

    @property
    def available(self) -> bool:
        return self.status.enabled
