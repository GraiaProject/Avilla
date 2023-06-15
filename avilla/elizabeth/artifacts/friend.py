from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.spec.core.activity.skeleton import ActivityTrigger
from avilla.spec.core.message import MessageRevoke, MessageSend
from avilla.spec.core.profile.metadata import Nick, Summary

from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull

if TYPE_CHECKING:
    from graia.amnesia.message import MessageChain

    from avilla.core.context import Context

    from ..protocol import ElizabethProtocol


with bounds("friend"):
    # casts(MessageSend)
    # casts(MessageRevoke)

    @implement(MessageSend.send)
    async def send_friend_message(
        cx: Context, target: Selector, message: MessageChain, *, reply: Selector | None = None
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(cx.protocol, ElizabethProtocol)
        serialized_msg = await cx.protocol.serialize_message(message)
        result = await cx.account.call(
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
            scene=Selector().land(cx.land).friend(str(target.pattern["friend"])),
            content=message,
            time=datetime.now(),
            sender=cx.account.to_selector(),
        )
        message_selector = message_metadata.to_selector()
        cx._collect_metadatas(message_selector, message_metadata)
        return message_selector

    @implement(MessageRevoke.revoke)
    async def revoke_friend_message(cx: Context, message: Selector):
        await cx.account.call(
            "recall",
            {
                "__method__": "update",
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["friend"]),
            },
        )

    @pull(Summary)
    async def get_friend_summary(cx: Context, target: Selector):
        result = await cx.account.call(
            "friendProfile",
            {
                "__method__": "fetch",
                "target": int(target.pattern["friend"]),
            },
        )
        return Summary(result["nickname"], "a friend contact assigned to this account")

    @pull(Nick)
    async def get_friend_nick(cx: Context, target: Selector):
        result = await cx.account.call(
            "friendProfile",
            {
                "__method__": "fetch",
                "target": int(target.pattern["friend"]),
            },
        )
        return Nick(result["nickname"], result["nickname"], None)


with bounds("friend.nudge"):

    @implement(ActivityTrigger.trigger)
    async def send_member_nudge(cx: Context, target: Selector):
        await cx.account.call(
            "sendNudge",
            {
                "__method__": "update",
                "target": int(target["friend"]),
                "subject": int(target["friend"]),
                "kind": "Friend",
            },
        )
