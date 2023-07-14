from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived

from ...staff import ElizabethStaff

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethEventMessagePerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @EventParse.collect(m, "FriendMessage")
    async def friend(self, raw_event: dict):
        friend = Selector().land(self.account.route["land"]).friend(str(raw_event["sender"]["id"]))
        message_result = await ElizabethStaff(self.account).deserialize_message(raw_event["messageChain"])

        return MessageReceived(
            Context(
                self.account,
                friend,
                friend,
                friend,
                self.account.route,
            ),
            Message(
                id=message_result["source"],
                scene=friend,
                sender=friend,
                content=message_result["content"],
                time=message_result["time"],
                reply=friend.appendix("message", message_result["reply"]) if message_result["reply"] else None,
            ),
        )


    @EventParse.collect(m, "GroupMessage")
    async def group(self, raw_event: dict):
        group = Selector().land(self.account.route["land"]).group(str(raw_event["sender"]["group"]["id"]))
        member = group.member(str(raw_event["sender"]["id"]))
        message_result = await ElizabethStaff(self.account).deserialize_message(raw_event["messageChain"])
        return MessageReceived(
            Context(
                self.account,
                member,
                group,
                group,
                self.account.route,
            ),
            Message(
                id=message_result["source"],
                scene=group,
                sender=member,
                content=message_result["content"],
                time=message_result["time"],
                reply=group.appendix("message", message_result["reply"]) if message_result["reply"] else None,
            ),
        )
