from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.telegram.me.capability import MeCapability

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramMeActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "me"

    @m.entity(MeCapability.get_me, target="land")
    async def get_me(self) -> ...:
        return await self.account.instance.bot.get_me()

    @m.entity(MeCapability.get_my_commands, target="land")
    async def get_my_commands(self, *, scope: str = None, language_code: str = None) -> ...:
        return await self.account.instance.bot.get_my_commands(scope, language_code)

    @m.entity(MeCapability.get_my_description, target="land")
    async def get_my_description(self, *, language_code: str = None) -> str:
        return await self.account.instance.bot.get_my_description(language_code)

    @m.entity(MeCapability.get_my_short_description, target="land")
    async def get_my_short_description(self, *, language_code: str = None) -> str:
        return await self.account.instance.bot.get_my_short_description(language_code)

    @m.entity(MeCapability.get_my_name, target="land")
    async def get_my_name(self, *, language_code: str = None) -> str:
        return await self.account.instance.bot.get_my_name(language_code)
