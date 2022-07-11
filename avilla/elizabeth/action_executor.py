from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.action import IterateMembers, MessageSend
from avilla.core.relationship import Relationship
from avilla.core.utilles.action_executor import ProtocolActionExecutor, action
from avilla.core.utilles.selector import Selector
from avilla.elizabeth.connection import ConnectionInterface
from avilla.elizabeth.connection.util import CallMethod

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethGroupActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=Selector(mode="exist").group("*")
):
    @action(MessageSend)
    async def send_message(self, action: MessageSend, relationship: Relationship):
        message = await self.protocol.serialize_message(action.message)
        interface = relationship.protocol.avilla.launch_manager.get_interface(ConnectionInterface)
        interface = interface.bind(int(relationship.current.pattern["account"]))
        result = await interface.call(
            "sendGroupMessage",
            CallMethod.POST,
            {
                "target": int(action.target.pattern["group"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            },
        )
        return action.target.mix("land.group.message", message=result["messageId"])

    @action(IterateMembers)
    async def iterate_members(self, action: IterateMembers, relationship: Relationship):
        interface = relationship.protocol.avilla.launch_manager.get_interface(ConnectionInterface)
        interface = interface.bind(int(relationship.current.pattern["account"]))
        result: list[dict] = await interface.call(
            "memberList",
            CallMethod.GET,
            {"target": int(action.mainline.pattern["group"])},
        )

        async def member_iterate():
            for i in result:
                yield action.mainline.mix("land.group.member", member=i["id"])

        return member_iterate()


class ElizabethFriendActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=Selector(mode="fragment").friend("*")
):
    @action(MessageSend)
    async def send_message(self, action: MessageSend, relationship: Relationship):
        message = await self.protocol.serialize_message(action.message)
        interface = relationship.protocol.avilla.launch_manager.get_interface(ConnectionInterface)
        interface = interface.bind(int(relationship.current.pattern["account"]))
        result = await interface.call(
            "sendFriendMessage",
            CallMethod.POST,
            {
                "target": int(action.target.pattern["friend"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            },
        )
        return action.target.mix("land.friend.message", message=result["messageId"])


class ElizabethGroupMemberActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=Selector(mode="fragment").group("*").member("*")
):
    @action(MessageSend)
    async def send_message(self, action: MessageSend, relationship: Relationship):
        message = await self.protocol.serialize_message(action.message)
        interface = relationship.protocol.avilla.launch_manager.get_interface(ConnectionInterface)
        interface = interface.bind(int(relationship.current.pattern["account"]))
        result = await interface.call(
            "sendTempMessage",
            CallMethod.POST,
            {
                "target": int(action.target.pattern["group"]),
                "qq": int(action.target.pattern["member"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            },
        )
        return action.target.mix("land.group.member.message", message=result["messageId"])
