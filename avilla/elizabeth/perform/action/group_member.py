from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethGroupMemberActionPerform((m := ContextCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @m.pull("lang.group.member", Nick)
    async def get_group_member_nick(self, target: Selector) -> Nick:
        result = await self.account.connection.call(
            "fetch",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )
        assert result is not None
        return Nick(result["memberName"], result["memberName"], result.get("specialTitle"))
