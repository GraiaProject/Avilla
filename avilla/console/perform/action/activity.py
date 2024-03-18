from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.selector import Selector
from avilla.standard.core.activity import start_activity
from flywheel import scoped_collect
from avilla.console.bases import InstanceOfAccount

if TYPE_CHECKING:
    from avilla.console.account import ConsoleAccount  # noqa
    from avilla.console.protocol import ConsoleProtocol  # noqa


class ConsoleActivityActionPerform(m := scoped_collect.env().target, InstanceOfAccount):
    @m.impl(start_activity, target="land.user.activity(bell)")
    async def bell(self, target: Selector | None = None):
        await self.account.client.call("bell", {})
