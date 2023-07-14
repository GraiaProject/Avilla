from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, TypedDict, cast

from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message, MessageChain
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived
from avilla.core.ryanvk.staff import Staff
from avilla.core.ryanvk.descriptor.event import EventParse

from ...collector.connection import ConnectionCollector

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa

class MessageDeserializeResult(TypedDict):
    content: MessageChain
    source: str
    time: datetime
    reply: str | None


class ElizabethEventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    async def _deserialize_message(self, raw_elements: list[dict]):
        result: dict[str, Any] = {
            "source": str(raw_elements[0]["id"]),
            "time": datetime.fromtimestamp(raw_elements[0]["time"]),
        }
        for index, raw_element in enumerate(raw_elements[1:]):
            element_type = raw_element["type"]
            if element_type == "Quote":
                result["reply"] = str(raw_element["id"])
                raw_elements.pop(index + 1)
                break
        result["content"] = await Staff(self.connection).deserialize_message(raw_elements[1:])
        return cast(MessageDeserializeResult, result)

    @EventParse.collect(m, "FriendMessage")
    async def friend(self, raw_event: dict):
        account = Selector().land("qq").account(str(self.connection.account_id))
        friend = Selector().land(account["land"]).friend(str(raw_event["sender"]["id"]))
        message_result = await self._deserialize_message(raw_event["messageChain"])

        return MessageReceived(
            Context(
                self.protocol.avilla.accounts[account].account,
                friend,
                friend,
                friend,
                account,
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
        account = Selector().land("qq").account(str(self.connection.account_id))
        group = Selector().land(account["land"]).group(str(raw_event["sender"]["group"]["id"]))
        member = group.member(str(raw_event["sender"]["id"]))
        message_result = await self._deserialize_message(raw_event["messageChain"])
        return MessageReceived(
            Context(
                self.protocol.avilla.accounts[account].account,
                member,
                group,
                group,
                account,
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
