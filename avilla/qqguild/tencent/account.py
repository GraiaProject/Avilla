from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.account import BaseAccount, AccountStatus
from avilla.qqguild.tencent.connection.base import QQGuildNetworking
from ...core import Selector

if TYPE_CHECKING:
    from .protocol import QQGuildProtocol


@dataclass
class QQGuildAccount(BaseAccount):
    protocol: QQGuildProtocol
    connection: QQGuildNetworking

    def __init__(self, route: Selector, protocol: QQGuildProtocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()

    @property
    def available(self) -> bool:
        return self.connection.alive
