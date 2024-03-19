from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick, Summary
from avilla.console.bases import InstanceOfAccount
from flywheel import scoped_collect

from avilla.core.builtins.capability import CoreCapability

if TYPE_CHECKING:
    from avilla.console.account import ConsoleAccount  # noqa
    from avilla.console.protocol import ConsoleProtocol  # noqa


class ConsoleProfileActionPerform(m := scoped_collect.env().target, InstanceOfAccount, static=True):
    @m.impl(CoreCapability.pull, "lang.user", Nick)
    async def get_console_nick(self, target: Selector) -> Nick:
        console = self.account.client.storage.current_user
        return Nick(console.nickname, console.nickname, "")

    @m.impl(CoreCapability.pull, "lang.user", Summary)
    async def get_summary(self, target: Selector) -> Summary:
        console = self.account.client.storage.current_user
        return Summary(console.nickname, console.nickname)
