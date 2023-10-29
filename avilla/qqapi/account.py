from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector
from avilla.qqapi.connection.base import QQAPINetworking

if TYPE_CHECKING:
    from .protocol import QQAPIProtocol


@dataclass
class QQAPIAccount(BaseAccount):
    protocol: QQAPIProtocol
    connection: QQAPINetworking

    def __init__(self, route: Selector, protocol: QQAPIProtocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()

    @property
    def available(self) -> bool:
        return self.connection.alive
