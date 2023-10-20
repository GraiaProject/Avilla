from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.activity import ActivityTrigger

if TYPE_CHECKING:
    from avilla.console.account import ConsoleAccount  # noqa
    from avilla.console.protocol import ConsoleProtocol  # noqa


class ConsoleActivityActionPerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.namespace = "avilla.protocol/console::action/activity"

    @m.entity(ActivityTrigger.trigger, target="land.user.activity(bell)")
    async def bell(self, target: Selector | None = None):
        await self.account.client.call("bell", {})
