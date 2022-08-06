from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avilla.core.action import MessageRevoke, MessageSend, StandardActionImpl
from avilla.core.relationship import RelationshipExecutor
from avilla.core.utilles.action_executor import ProtocolActionExecutor
from avilla.core.utilles.selector import DynamicSelector

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethGroupActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=DynamicSelector.fragment().group("*")
):
    class SendMessageImpl(StandardActionImpl):
        endpoint = "sendGroupMessage"
        actions = [MessageSend]

        @staticmethod
        async def get_execute_params(executor: RelationshipExecutor[MessageSend]) -> dict[str, Any]:
            action = executor.action
            message = await executor.relationship.protocol.serialize_message(action.message)
            return {
                "__method__": "post",
                "target": int(action.target.pattern["group"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            }
        
        @staticmethod
        def unwrap_result(executor: RelationshipExecutor[MessageSend], result: Any) -> Any:
            return executor.action.target.mix("land.group.message", message=result["messageId"])

    class RevokeMessageImpl(StandardActionImpl):
        endpoint = "revokeGroupMessage"
        actions = [MessageRevoke]

        @staticmethod
        async def get_execute_params(executor: RelationshipExecutor[MessageRevoke]) -> dict[str, Any]:
            action = executor.action
            return {
                "__method__": "post",
                "target": int(action.message.pattern["message"]),
            }
        
        @staticmethod
        def unwrap_result(executor: Any, result: Any) -> Any:
            return


class ElizabethFriendActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=DynamicSelector.fragment().friend("*")
):
    class SendMessageImpl(StandardActionImpl):
        endpoint = "sendFriendMessage"
        actions = [MessageSend]

        @staticmethod
        async def get_execute_params(executor: RelationshipExecutor[MessageSend]) -> dict[str, Any]:
            action = executor.action
            message = await executor.relationship.protocol.serialize_message(action.message)
            return {
                "__method__": "post",
                "target": int(action.target.pattern["friend"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            }
        
        @staticmethod
        def unwrap_result(executor: RelationshipExecutor[MessageSend], result: Any) -> Any:
            return executor.action.target.mix("land.friend.message", message=result["messageId"])


class ElizabethGroupMemberActionExecutor(
    ProtocolActionExecutor["ElizabethProtocol"], pattern=DynamicSelector.fragment().group("*").member("*")
):
    class SendMessageImpl(StandardActionImpl):
        endpoint = "sendGroupMessage"
        actions = [MessageSend]

        @staticmethod
        async def get_execute_params(executor: RelationshipExecutor[MessageSend]) -> dict[str, Any]:
            action = executor.action
            message = await executor.relationship.protocol.serialize_message(action.message)
            return {
                "__method__": "post",
                "target": int(action.target.pattern["group"]),
                "qq": int(action.target.pattern["member"]),
                "messageChain": message,
                **({"quote": action.reply.pattern["message"]} if action.reply is not None else {}),
            }
        
        @staticmethod
        def unwrap_result(executor: RelationshipExecutor[MessageSend], result: Any) -> Any:
            return executor.action.target.mix("land.group.member.message", message=result["messageId"])
