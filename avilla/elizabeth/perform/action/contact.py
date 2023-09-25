from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick, Summary

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethContactActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::action"
    m.identify = "contact"

    @m.pull("land.contact", Nick)
    async def get_contact_nick(self, target: Selector, route: ...) -> Nick:
        result = await self.account.connection.call(
            "fetch",
            "userProfile",
            {
                "target": int(target.pattern["contact"]),
            },
        )
        return Nick(result["nickname"], result["nickname"], None)

    @m.pull("land.contact", Summary)
    async def get_contact_summary(self, target: Selector, route: ...) -> Summary:
        result = await self.account.connection.call(
            "fetch",
            "userProfile",
            {
                "target": int(target.pattern["contact"]),
            },
        )
        return Summary(result["nickname"], "a strange contact on platform qq")
