from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick, Summary

if TYPE_CHECKING:
    from avilla.console.account import ConsoleAccount  # noqa
    from avilla.console.protocol import ConsoleProtocol  # noqa


class ConsoleProfileActionPerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.namespace = "avilla.protocol/console::action/profile"

    @m.pull("lang.user", Nick)
    async def get_console_nick(self, target: Selector, route: type[Nick]) -> Nick:
        console = self.account.client.storage.current_user
        return Nick(console.nickname, console.nickname, "")

    @m.pull("lang.user", Summary)
    async def get_summary(self, target: Selector, route: type[Summary]) -> Summary:
        console = self.account.client.storage.current_user
        return Summary(console.nickname, console.nickname)
