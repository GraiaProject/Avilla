from __future__ import annotations
from typing import TYPE_CHECKING

from ...core.utilles.selector import Selector
from ...core.context import Context

from avilla.elizabeth.util import event
from avilla.spec.core.message import MessageReceived
from avilla.core.abstract.message import Message

if TYPE_CHECKING:
    from ..protocol import ElizabethProtocol
    from ..account import ElizabethAccount


@event("GroupMessage")
async def group_message(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict):
    group = Selector().land(protocol.land.name).group(str(raw["sender"]["group"]["id"]))
    context = Context(
        account=account,
        client=group._.member(str(raw["sender"]["id"])),
        endpoint=group,
        scene=group,
        selft=group._.member(account.id),
    )
    message_result = await protocol.deserialize_message(context, raw["messageChain"])
    event = MessageReceived(
        context, Message(describe=Message, id=message_result["source"], scene=group, time=message_result["time"])
    )
    return event, context


@event("FriendMessage")
async def friend_message(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict):
    friend = Selector().land(protocol.land.name).friend(str(raw["sender"]["id"]))
    context = Context(
        account=account,
        client=friend,
        endpoint=friend,
        scene=friend,
        selft=account.to_selector(),
    )
    message_result = await protocol.deserialize_message(context, raw["messageChain"])
    event = MessageReceived(
        context, Message(describe=Message, id=message_result["source"], scene=friend, time=message_result["time"])
    )
    return event, context


@event("TempMessage")
async def temp_message(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict):
    group = Selector().land(protocol.land.name).group(str(raw["sender"]["group"]["id"]))
    member = group._.member(str(raw["sender"]["id"]))
    context = Context(
        account=account,
        client=member,
        endpoint=member,
        scene=member,
        selft=group._.member(account.id),
    )
    message_result = await protocol.deserialize_message(context, raw["messageChain"])
    event = MessageReceived(
        context, Message(describe=Message, id=message_result["source"], scene=member, time=message_result["time"])
    )
    return event, context
