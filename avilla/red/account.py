from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector
from avilla.standard.core.account import AccountAvailable, AccountUnavailable

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

    @contextmanager
    def _status_update(self):
        prev = self.available
        yield
        if prev != (curr := self.available):
            avilla = self.protocol.avilla
            avilla.broadcast.postEvent((AccountAvailable if curr else AccountUnavailable)(avilla, self))

    @property
    def available(self) -> bool:
        return self.status.enabled
