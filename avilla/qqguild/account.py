from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.account import BaseAccount
from avilla.qqguild.connection.base import QQGuildNetworking

if TYPE_CHECKING:
    from .protocol import QQGuildProtocol


@dataclass
class QQGuildAccount(BaseAccount):
    protocol: QQGuildProtocol

    @property
    def connection(self) -> QQGuildNetworking:
        return self.protocol.service.get_connection(self.route["account"])

    @property
    def available(self) -> bool:
        return self.connection.alive
