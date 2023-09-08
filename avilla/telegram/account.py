from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.account import AccountStatus, BaseAccount
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.telegram.bot.bot import TelegramBot
    from avilla.telegram.protocol import TelegramProtocol


@dataclass
class TelegramAccount(BaseAccount):
    protocol: TelegramProtocol
    status: AccountStatus

    def __init__(self, route: Selector, protocol: TelegramProtocol):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()

    @property
    def instance(self) -> TelegramBot:
        return self.protocol.service.get_instance(int(self.route["account"]))

    @property
    def available(self) -> bool:
        return self.instance.available
