from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from .net.base import RedNetworking
    from .protocol import RedProtocol


class RedAccount(BaseAccount):
    protocol: RedProtocol
    status: AccountStatus
    websocket_client: RedNetworking

    def __init__(self, route: Selector, protocol: RedProtocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()

    @property
    def available(self) -> bool:
        return self.status.enabled
