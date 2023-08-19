from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, TypedDict, cast

from avilla.core.context import Context
from avilla.core.message import Message, MessageChain
from avilla.core.selector import Selector
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.elizabeth.const import PRIVILEGE_LEVEL
from avilla.standard.core.message import MessageReceived, MessageRevoked
from avilla.standard.core.privilege import MuteInfo, Privilege
from avilla.standard.core.profile import Nick, Summary

from . import ElizabethEventParse


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
        result["content"] = await account.staff.ext({"context": context}).deserialize_message(raw_elements[1:])
        return cast(MessageDeserializeResult, result)

    @m.entity(ElizabethEventParse, "FriendMessage")
    async def friend(self, raw_event: dict):
        account = Selector().land("qq").account(str(self.connection.account_id))
        friend = Selector().land(account["land"]).friend(str(raw_event["sender"]["id"]))
        context = Context(
            self.protocol.avilla.accounts[account].account,
            friend,
            account,
            friend,
            account,
        )
        message_result = await self._deserialize_message(context, raw_event["messageChain"])
        sender = raw_event["sender"]
        context._collect_metadatas(
            friend,
            Nick(sender["nickname"], sender["remark"] or sender["nickname"], None),
            Summary(sender["nickname"], "a friend contact assigned to this account"),
        )
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

    @m.entity(ElizabethEventParse, "GroupMessage")
    async def group(self, raw_event: dict):
        account = Selector().land("qq").account(str(self.connection.account_id))
        sender = raw_event["sender"]
        group_data = sender["group"]
        group = Selector().land(account["land"]).group(str(group_data["id"]))
        member = group.member(str(sender["id"]))
        context = Context(
            self.protocol.avilla.accounts[account].account,
            member,
            group,
            group,
            group.member(str(account["account"])),
        )
        context._collect_metadatas(
            member,
            Nick(sender["memberName"], sender["memberName"], sender.get("specialTitle")),
            Summary(sender["memberName"], "a group member assigned to this account"),
            MuteInfo(
                sender.get("mutetimeRemaining") is not None,
                timedelta(seconds=sender.get("mutetimeRemaining", 0)),
                None,
            ),
            Privilege(
                PRIVILEGE_LEVEL[sender["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[sender["permission"]],
            ),
        )
        context._collect_metadatas(
            group,
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
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

    @m.entity(ElizabethEventParse, "FriendRecallEvent")
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

    @m.entity(ElizabethEventParse, "GroupRecallEvent")
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
            .group(str(raw_event["group"]["id"]))
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
        group_data = raw_event["group"]
        if operator:
            context._collect_metadatas(
                member,
                Nick(operator["memberName"], operator["memberName"], operator.get("specialTitle")),
                Summary(operator["memberName"], "a group member assigned to this account"),
                MuteInfo(
                    operator.get("mutetimeRemaining") is not None,
                    timedelta(seconds=operator.get("mutetimeRemaining", 0)),
                    None,
                ),
                Privilege(
                    PRIVILEGE_LEVEL[operator["permission"]] > 0,
                    PRIVILEGE_LEVEL[group_data["permission"]] > PRIVILEGE_LEVEL[operator["permission"]],
                ),
            )
        context._collect_metadatas(
            member,
            Summary(group_data["name"], None),
            Privilege(
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
                PRIVILEGE_LEVEL[group_data["permission"]] > 0,
            ),
        )
        return MessageRevoked(
            context,
            message,
            member,
        )
