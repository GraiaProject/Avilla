from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.account import BaseAccount

if TYPE_CHECKING:
    from avilla.telegram.connection.poll import TelegramNetworking
    from avilla.telegram.protocol import TelegramProtocol


@dataclass
class TelegramAccount(BaseAccount):
    protocol: TelegramProtocol

    @property
    def connection(self) -> TelegramNetworking:
        return self.protocol.service.get_connection(int(self.route["account"]))

    @property
    def available(self) -> bool:
        return self.connection.alive
