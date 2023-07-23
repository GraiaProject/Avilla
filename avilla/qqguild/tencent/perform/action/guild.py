from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.common import Count
from avilla.standard.core.profile import Summary

if TYPE_CHECKING:
    from avilla.qqguild.tencent.account import QQGuildAccount  # noqa
    from avilla.qqguild.tencent.protocol import QQGuildProtocol  # noqa


class QQGuildGuildActionPerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    @m.pull("land.guild", Summary)
    async def get_summary(self, target: Selector) -> Summary:
        result = await self.account.connection.call("get", f"guilds/{target.pattern['guild']}", {})
        return Summary(result["name"], result["description"])

    @m.pull("land.guild", Count)
    async def get_count(self, target: Selector) -> Count:
        result = await self.account.connection.call("get", f"guilds/{target.pattern['guild']}", {})
        return Count(result["member_count"], result["max_members"])
