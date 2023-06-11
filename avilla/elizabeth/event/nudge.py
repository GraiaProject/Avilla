from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder
from avilla.spec.core.activity.event import ActivityTrigged

if TYPE_CHECKING:
    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


event = EventParserRecorder["ElizabethProtocol", "ElizabethAccount"]


@event("NudgeEvent")
async def nudge_event(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict):
    if raw["context_type"] == "group":
        group = Selector().land(protocol.land).group(str(raw["subject"]["id"]))
        operator = group.member(str(raw["fromId"]))
        target = group.member(str(raw["target"]))
        selft = group.member(account.id)
        context = Context(account, operator, target.nudge("..."), group, selft)
    elif raw["context_type"] == "friend":
        friend = Selector().land(protocol.land).friend(str(raw["subject"]["id"]))
        target = account.to_selector() if str(raw["target"]) == account.id else friend
        context = Context(account, friend, target.nudge("..."), friend, account.to_selector())
    else:
        raise NotImplementedError

    return ActivityTrigged(context, Selector().land(protocol.land).activity("nudge"), context.endpoint), context
