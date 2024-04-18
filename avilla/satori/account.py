from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from satori.client.account import Account

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from .protocol import SatoriProtocol


@dataclass
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

    # @contextmanager
    # def _status_update(self):
    #     prev = self.available
    #     yield
    #     if prev != (curr := self.available):
    #         avilla = self.protocol.avilla
    #         avilla.broadcast.postEvent((AccountAvailable if curr else AccountUnavailable)(avilla, self))

    @property
    def available(self) -> bool:
        return self.client.connected.is_set()
