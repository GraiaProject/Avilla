from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector
from avilla.standard.core.account import AccountAvailable, AccountUnavailable

from satori.account import Account

if TYPE_CHECKING:
    from .protocol import SatoriProtocol


class SatoriAccount(BaseAccount):
    protocol: SatoriProtocol
    status: AccountStatus
    client: Account

    def __init__(self, route: Selector, protocol: SatoriProtocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()

    @property
    def identity(self):
        return f"{self.route['land']}/{self.route['account']}"

    @contextmanager
    def _status_update(self):
        prev = self.available
        yield
        if prev != (curr := self.available):
            avilla = self.protocol.avilla
            avilla.broadcast.postEvent((AccountAvailable if curr else AccountUnavailable)(avilla, self))

    @property
    def available(self) -> bool:
        return self.client.connected.is_set()
