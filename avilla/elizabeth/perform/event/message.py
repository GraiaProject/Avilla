from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict, cast

from avilla.core.context import Context
from avilla.core.message import Message, MessageChain
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.standard.core.message import MessageReceived, MessageRevoked


class MessageDeserializeResult(TypedDict):
    content: MessageChain
    source: str
    time: datetime
    reply: str | None


class ElizabethEventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    async def _deserialize_message(self, context: Context, raw_elements: list[dict]):
        result: dict[str, Any] = {
            "source": str(raw_elements[0]["id"]),
            "time": datetime.fromtimestamp(raw_elements[0]["time"]),
            "reply": None,
        }
        for index, raw_element in enumerate(raw_elements[1:]):
            element_type = raw_element["type"]
            if element_type == "Quote":
                result["reply"] = str(raw_element["id"])
                raw_elements.pop(index + 1)
                break
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        result["content"] = await account.staff.x({"context": context}).deserialize_message(raw_elements[1:])
        return cast(MessageDeserializeResult, result)

    @EventParse.collect(m, "FriendMessage")
    async def friend(self, raw_event: dict):
        account = Selector().land("qq").account(str(self.connection.account_id))
        friend = Selector().land(account["land"]).friend(str(raw_event["sender"]["id"]))
        context = Context(
            self.protocol.avilla.accounts[account].account,
            friend,
            friend,
            friend,
            account,
        )
        message_result = await self._deserialize_message(context, raw_event["messageChain"])

        return MessageReceived(
            context,
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
        context = Context(
            self.protocol.avilla.accounts[account].account,
            member,
            group,
            group,
            group.member(str(account["account"])),
        )
        message_result = await self._deserialize_message(context, raw_event["messageChain"])
        return MessageReceived(
            context,
            Message(
                id=message_result["source"],
                scene=group,
                sender=member,
                content=message_result["content"],
                time=message_result["time"],
                reply=group.appendix("message", message_result["reply"]) if message_result["reply"] else None,
            ),
        )

    @EventParse.collect(m, "FriendRecallEvent")
    async def friend_recall(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        friend = Selector().land("qq").friend(str(raw_event["operator"]))
        message = Selector().land("qq").friend(str(raw_event["authorId"])).message(str(raw_event["messageId"]))
        context = Context(
            account,
            friend,
            friend,
            friend,
            account_route,
        )
        return MessageRevoked(
            context,
            message,
            friend,
        )

    @EventParse.collect(m, "GroupRecallEvent")
    async def group_recall(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        group = Selector().land("qq").group(str(raw_event["group"]["id"]))
        if operator := raw_event.get("operator"):
            member = group.member(str(operator["id"]))
        else:
            member = group.member(account_route["account"])
        message = (
            Selector()
            .land("qq")
            .group(str(raw_event["groupId"]))
            .member(str(raw_event["authorId"]))
            .message(str(raw_event["messageId"]))
        )
        context = Context(
            account,
            member,
            group,
            group,
            group.member(account_route["account"]),
        )
        return MessageRevoked(
            context,
            message,
            member,
        )
