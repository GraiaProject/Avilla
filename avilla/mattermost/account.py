from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector
from avilla.mattermost.connection.base import MattermostNetworking

if TYPE_CHECKING:
    from avilla.mattermost.protocol import MattermostProtocol


@dataclass
class MattermostAccount(BaseAccount):
    protocol: MattermostProtocol
    status: AccountStatus

    def __init__(self, route: Selector, protocol: MattermostProtocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()

    @property
    def connection(self) -> MattermostNetworking:
        return self.protocol.service.get_connection(self.route["account"])

    @property
    def available(self) -> bool:
        return self.connection.alive
