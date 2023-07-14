from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick, Summary

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethFriendActionPerform((m := ContextCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @m.pull("lang.friend", Nick)
    async def get_contact_nick(self, target: Selector) -> Nick:
        result = await self.account.connection.call(
            "fetch",
            "friendProfile",
            {
                "target": int(target.pattern["friend"]),
            },
        )
        assert result is not None
        return Nick(result["nickname"], result["nickname"], None)

    @m.pull("lang.friend", Summary)
    async def get_contact_summary(self, target: Selector) -> Summary:
        result = await self.account.connection.call(
            "fetch",
            "friendProfile",
            {
                "target": int(target.pattern["friend"]),
            },
        )
        assert result is not None
        return Summary(result["nickname"], "a friend contact assigned to this account")
