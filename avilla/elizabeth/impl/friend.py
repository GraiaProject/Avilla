from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.abstract.trait.context import bounds, implement
from avilla.core.utilles.selector import Selector
from avilla.spec.core.message import MessageRevoke, MessageSend

if TYPE_CHECKING:
    from graia.amnesia.message import MessageChain

    from avilla.core.context import Context
    from ..protocol import ElizabethProtocol

# raise_for_no_namespace()

# with scope("qq", "friend"), prefix("friend"):
with bounds("friend"):  # maybe problem

    # casts(MessageSend)
    # casts(MessageRevoke)

    @implement(MessageSend.send)
    async def send_friend_message(
        ctx: Context, target: Selector, message: MessageChain, *, reply: Selector | None = None
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(ctx.protocol, ElizabethProtocol)
        serialized_msg = await ctx.protocol.serialize_message(message)
        result = await ctx.account.call(
            "sendFriendMessage",
            {
                "__method__": "post",
                "target": int(target.pattern["friend"]),
                "messageChain": serialized_msg,
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        return Selector().land(ctx.land).group(target.pattern["friend"]).message(result["messageId"])

    @implement(MessageRevoke.revoke)
    async def revoke_friend_message(ctx: Context, message: Selector):
        await ctx.account.call(
            "recall",
            {
                "__method__": "post",
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["friend"]),
            },
        )
