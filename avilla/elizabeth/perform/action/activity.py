from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.activity import ActivityTrigger

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethActivityActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::action"
    m.identify = "activity"

    @m.entity(ActivityTrigger.trigger, target="land.friend.activity(nudge)")
    async def friend_nudge(self, target: Selector):
        await self.account.connection.call(
            "update",
            "sendNudge",
            {
                "target": int(target["friend"]),
                "subject": int(target["friend"]),
                "kind": "Friend",
            },
        )

    @m.entity(ActivityTrigger.trigger, target="land.group.member.activity(nudge)")
    async def group_nudge(self, target: Selector):
        await self.account.connection.call(
            "update",
            "sendNudge",
            {
                "target": int(target["member"]),
                "subject": int(target["group"]),
                "kind": "Group",
            },
        )
