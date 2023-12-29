from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector
from avilla.elizabeth.connection.base import ElizabethNetworking

if TYPE_CHECKING:
    from avilla.elizabeth.protocol import ElizabethProtocol


@dataclass
class ElizabethAccount(BaseAccount):
    protocol: ElizabethProtocol
    status: AccountStatus

    def __init__(self, route: Selector, protocol: ElizabethProtocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()

    @property
    def connection(self) -> ElizabethNetworking:
        return self.protocol.service.get_connection(self.route["account"])

    @property
    def available(self) -> bool:
        return self.connection.alive
