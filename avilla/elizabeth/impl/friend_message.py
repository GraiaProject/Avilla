from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement
from avilla.spec.core.message import MessageRevoke

if TYPE_CHECKING:
    from graia.amnesia.message import __message_chain_class__

    from avilla.core.context import Context

with bounds("friend.message"):
    @implement(MessageRevoke.revoke)
    async def revoke_friend_message(ctx: Context, message_selector: Selector):
        await ctx.account.call(
            "recall",
            {
                "__method__": "update",
                "messageId": int(message_selector.last_value),
                "target": int(message_selector['friend'])
            },
        )
