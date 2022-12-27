from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull
from avilla.spec.core.activity.skeleton import ActivityTrigger
from avilla.spec.core.message import MessageRevoke, MessageSend
from avilla.spec.core.profile.metadata import Nick, Summary

if TYPE_CHECKING:
    from graia.amnesia.message import __message_chain_class__

    from avilla.core.context import Context

    from ..protocol import ElizabethProtocol


with bounds("friend"):

    # casts(MessageSend)
    # casts(MessageRevoke)

    @implement(MessageSend.send)
    async def send_friend_message(
        ctx: Context, target: Selector, message: __message_chain_class__, *, reply: Selector | None = None
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(ctx.protocol, ElizabethProtocol)
        serialized_msg = await ctx.protocol.serialize_message(message)
        result = await ctx.account.call(
            "sendFriendMessage",
            {
                "__method__": "update",
                "target": int(target.pattern["friend"]),
                "messageChain": serialized_msg,
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        message_metadata = Message(
            id=str(result["messageId"]),
            scene=Selector().land(ctx.land).friend(str(target.pattern["friend"])),
            content=message,
            time=datetime.now(),
            sender=ctx.account.to_selector(),
        )
        message_selector = message_metadata.to_selector()
        ctx._collect_metadatas(message_selector, message_metadata)
        return message_selector

    @implement(MessageRevoke.revoke)
    async def revoke_friend_message(ctx: Context, message: Selector):
        await ctx.account.call(
            "recall",
            {
                "__method__": "update",
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["friend"]),
            },
        )

    @pull(Summary)
    async def get_friend_summary(ctx: Context, target: Selector):
        result = await ctx.account.call(
            "friendProfile",
            {
                "__method__": "fetch",
                "target": int(target.pattern["friend"]),
            },
        )
        return Summary(result["nickname"], "a friend contact assigned to this account")

    @pull(Nick)
    async def get_friend_nick(ctx: Context, target: Selector):
        result = await ctx.account.call(
            "friendProfile",
            {
                "__method__": "fetch",
                "target": int(target.pattern["friend"]),
            },
        )
        return Nick(result["nickname"], result["nickname"], None)


with bounds("friend.nudge"):

    @implement(ActivityTrigger.trigger)
    async def send_member_nudge(ctx: Context, target: Selector):
        await ctx.account.call(
            "sendNudge",
            {
                "__method__": "update",
                "target": int(target["friend"]),
                "subject": int(target["friend"]),
                "kind": "Friend",
            },
        )
