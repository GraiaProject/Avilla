from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.activity import ActivityTrigger

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa


class ConsoleActivityActionPerform(
    (m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._
):
    m.post_applying = True

    @ActivityTrigger.trigger.collect(m, "land.console.activity(bell)")
    async def bell(self, target: Selector | None = None):
        await self.account.client.call("bell", {})
