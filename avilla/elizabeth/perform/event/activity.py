from __future__ import annotations

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.standard.core.activity import ActivityTrigged

from . import ElizabethEventParse


class ElizabethEventActivityPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @m.entity(ElizabethEventParse, "NudgeEvent")
    async def nudge(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        if raw_event["subject"]["kind"] == "Group":
            group = land.group(str(raw_event["subject"]["id"]))
            sender = group.member(str(raw_event["fromId"]))
            target = group.member(str(raw_event["target"]))
            context = Context(
                account,
                sender,
                target,
                group,
                group.member(account_route["account"]),
            )
            activity = sender.nudge(raw_event["action"])
            return ActivityTrigged(context, "nudge", group, activity, sender)
        else:
            friend = land.friend(str(raw_event["subject"]["id"]))
            context = Context(
                account,
                friend,
                account_route,
                friend,
                account_route,
            )
            activity = friend.nudge(raw_event["action"])
            return ActivityTrigged(context, "nudge", friend, activity, friend)
