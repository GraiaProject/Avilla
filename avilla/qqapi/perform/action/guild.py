from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.common import Count
from avilla.standard.core.profile import Nick, Summary

if TYPE_CHECKING:
    from avilla.qqapi.account import QQAPIAccount  # noqa
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIGuildActionPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::action"
    m.identify = "guild"

    @m.pull("land.guild", Summary)
    async def get_summary(self, target: Selector, route: ...) -> Summary:
        result = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}", {})
        return Summary(result["name"], result["description"])

    @m.pull("land.guild", Nick)
    async def get_nick(self, target: Selector, route: ...) -> Nick:
        result = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}", {})
        return Nick(result["name"], result["name"], None)

    @m.pull("land.guild", Count)
    async def get_count(self, target: Selector, route: ...) -> Count:
        result = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}", {})
        return Count(result["member_count"], result["max_members"])
