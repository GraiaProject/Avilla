from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.account import BaseAccount

if TYPE_CHECKING:
    from avilla.telegram.bot.bot import TelegramBot
    from avilla.telegram.protocol import TelegramProtocol


@dataclass
class TelegramAccount(BaseAccount):
    protocol: TelegramProtocol

    @property
    def instance(self) -> TelegramBot:
        return self.protocol.service.get_instance(int(self.route["account"]))

    @property
    def available(self) -> bool:
        return self.instance.available
