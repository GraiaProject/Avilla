from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick, Summary

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethFriendActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @m.pull("land.friend", Nick)
    async def get_contact_nick(self, target: Selector) -> Nick:
        result = await self.account.connection.call(
            "fetch",
            "friendProfile",
            {
                "target": int(target.pattern["friend"]),
            },
        )
        return Nick(result["nickname"], result["remark"] or result["nickname"], None)

    @m.pull("land.friend", Summary)
    async def get_contact_summary(self, target: Selector) -> Summary:
        result = await self.account.connection.call(
            "fetch",
            "friendProfile",
            {
                "target": int(target.pattern["friend"]),
            },
        )
        return Summary(result["nickname"], "a friend contact assigned to this account")

    # TODO: delete friend
