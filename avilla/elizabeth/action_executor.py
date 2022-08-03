from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.action import MessageRevoke, MessageSend
from avilla.core.relationship import Relationship
from avilla.core.utilles.action_executor import ProtocolActionExecutor, action
from avilla.core.utilles.selector import DynamicSelector
from avilla.elizabeth.account import ElizabethAccount

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethGroupActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=DynamicSelector.fragment().group("*")
):
    @action(MessageSend)
    async def send_message(self, action: MessageSend, relationship: Relationship):
        message = await self.protocol.serialize_message(action.message)
        account = relationship.current
        assert isinstance(account, ElizabethAccount)
        result = await account.call(
            "sendGroupMessage",
            {
                "__method__": "post",
                "target": int(action.target.pattern["group"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            },
        )
        return action.target.mix("land.group.message", message=result["messageId"])

    @action(MessageRevoke)
    async def revoke_message(self, action: MessageRevoke, relationship: Relationship):
        target_id: int = int(action.message.pattern["message"])
        account = relationship.current
        assert isinstance(account, ElizabethAccount)
        await account.call("recall", {"__method__": "post", "target": target_id})


class ElizabethFriendActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=DynamicSelector.fragment().friend("*")
):
    @action(MessageSend)
    async def send_message(self, action: MessageSend, relationship: Relationship):
        message = await self.protocol.serialize_message(action.message)
        account = relationship.current
        assert isinstance(account, ElizabethAccount)
        result = await account.call(
            "sendFriendMessage",
            {
                "__method__": "post",
                "target": int(action.target.pattern["friend"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            },
        )
        return action.target.mix("land.friend.message", message=result["messageId"])


class ElizabethGroupMemberActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=DynamicSelector.fragment().group("*").member("*")
):
    @action(MessageSend)
    async def send_message(self, action: MessageSend, relationship: Relationship):
        message = await self.protocol.serialize_message(action.message)
        account = relationship.current
        assert isinstance(account, ElizabethAccount)
        result = await account.call(
            "sendTempMessage",
            {
                "__method__": "post",
                "target": int(action.target.pattern["group"]),
                "qq": int(action.target.pattern["member"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            },
        )
        return action.target.mix("land.group.member.message", message=result["messageId"])
