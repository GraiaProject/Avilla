from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core import Context
from avilla.core.message import Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.elizabeth.capability import ElizabethCapability
from avilla.standard.core.message import (
    MessageReceived,
    MessageRevoke,
    MessageSend,
    MessageSent,
)

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethMessageActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::action"
    m.identify = "message"

    @m.entity(MessageSend.send, target="land.group")
    async def send_group_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        result = await self.account.connection.call(
            "update",
            "sendGroupMessage",
            {
                "target": int(target.pattern["group"]),
                "messageChain": [await self.staff.call_fn(ElizabethCapability.serialize_element, i) for i in message],
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        if result["msg"] != "success" or result["messageId"] < 0:
            raise RuntimeError(f"Failed to send message to {target.pattern['group']}: {message}")

        context = self.account.get_context(target.member(self.account.route["account"]))
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    result["messageId"],
                    target,
                    context.client,
                    message,
                    datetime.now(),
                ),
                self.account,
            )
        )
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message(result["messageId"])

    @m.entity(MessageSend.send, target="land.friend")
    async def send_friend_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        result = await self.account.connection.call(
            "update",
            "sendFriendMessage",
            {
                "target": int(target.pattern["friend"]),
                "messageChain": [await self.staff.call_fn(ElizabethCapability.serialize_element, i) for i in message],
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        if result["msg"] != "success" or result["messageId"] < 0:
            raise RuntimeError(f"Failed to send message to {target.pattern['friend']}: {message}")
        # context = self.account.get_context(target, via=self.account.route)
        context = Context(
            self.account,
            self.account.route,
            target,
            target,
            self.account.route,
        )
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    result["messageId"],
                    target,
                    context.client,
                    message,
                    datetime.now(),
                ),
                self.account,
            )
        )
        return Selector().land(self.account.route["land"]).friend(target.pattern["friend"]).message(result["messageId"])

    @m.entity(MessageRevoke.revoke, target="land.group.message")
    async def revoke_group_message(self, target: Selector):
        await self.account.connection.call(
            "update",
            "recall",
            {
                "messageId": int(target.pattern["message"]),
                "target": int(target.pattern["group"]),
            },
        )

    @m.entity(MessageRevoke.revoke, target="land.friend.message")
    async def revoke_friend_message(self, target: Selector):
        await self.account.connection.call(
            "update",
            "recall",
            {
                "messageId": int(target.pattern["message"]),
                "target": int(target.pattern["friend"]),
            },
        )

    @m.pull("land.group.message", Message)
    async def get_group_message(self, message: Selector, route: ...) -> Message:
        result = await self.account.connection.call(
            "fetch",
            "messageFromId",
            {
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["group"]),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to get message from {message.pattern['group']}: {message}")
        event = await self.account.staff.ext({"connection": self.account.connection}).call_fn(
            ElizabethCapability.event_callback, result
        )
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)  # noqa
        return event.message

    @m.pull("land.friend.message", Message)
    async def get_friend_message(self, message: Selector, route: ...) -> Message:
        result = await self.account.connection.call(
            "fetch",
            "messageFromId",
            {
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["friend"]),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to get message from {message.pattern['friend']}: {message}")
        event = await self.account.staff.ext({"connection": self.account.connection}).call_fn(
            ElizabethCapability.event_callback, result
        )
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)  # noqa
        return event.message
