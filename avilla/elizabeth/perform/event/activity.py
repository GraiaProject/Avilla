from __future__ import annotations

from avilla.core.context import Context
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.standard.core.activity import ActivityTrigged


class ElizabethEventActivityPerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "NudgeEvent")
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
            nudge = sender.activity("nudge")
            activity = sender.nudge("nudge").action(raw_event["action"]).suffix(raw_event["suffix"])
            return ActivityTrigged(context, nudge, activity, sender, group)
        else:
            friend = land.friend(str(raw_event["subject"]["id"]))
            context = Context(
                account,
                friend,
                account_route,
                friend,
                account_route,
            )
            nudge = friend.activity("nudge")
            activity = friend.nudge("nudge").action(raw_event["action"]).suffix(raw_event["suffix"])
            return ActivityTrigged(context, nudge, activity, friend, friend)
