from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Summary, Nick

if TYPE_CHECKING:
    from avilla.qqapi.account import QQAPIAccount  # noqa
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIUserActionPerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::action"
    m.identify = "user"

    @m.pull("land.guild.user", Summary)
    async def get_summary(self, target: Selector, route: ...) -> Summary:
        result = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}", {})
        return Summary(result["name"], result["description"])

    @m.pull("land.guild.user", Nick)
    async def get_nick(self, target: Selector, route: ...) -> Nick:
        result = await self.account.connection.call_http("get", f"guilds/{target.pattern['guild']}", {})
        return Nick(result["name"], result["name"], None)
