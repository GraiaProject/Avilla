from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.account import BaseAccount
from avilla.elizabeth.connection.base import ElizabethNetworking

if TYPE_CHECKING:
    from avilla.elizabeth.protocol import ElizabethProtocol


@dataclass
class ElizabethAccount(BaseAccount):
    protocol: ElizabethProtocol

    @property
    def connection(self) -> ElizabethNetworking:
        return self.protocol.service.get_connection(self.route["account"])

    @property
    def available(self) -> bool:
        return self.connection.alive
