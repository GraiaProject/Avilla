from __future__ import annotations
from typing import TYPE_CHECKING

from avilla.core.action import MessageSend
from avilla.core.relationship import Relationship
from avilla.core.utilles.action_executor import ProtocolActionExecutor, action
from avilla.core.utilles.selector import Selector
from avilla.elizabeth.connection import ConnectionInterface
from avilla.elizabeth.connection.util import CallMethod

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


class ElizabethFriendActionExecutor(ProtocolActionExecutor['ElizabethProtocol'], pattern=Selector(match_rule="exist").friend(lambda _: True)):
    @action(MessageSend)
    async def send_message(self, action: MessageSend, relationship: Relationship):
        message = await self.protocol.serialize_message(action.message)
        interface = relationship.protocol.avilla.launch_manager.get_interface(ConnectionInterface)
        interface = interface.bind(int(relationship.current.pattern['account']))
        # TODO: action.target dispatch
        await interface.call(
            "sendGroupMessage",
            CallMethod.POST,
            {
                "target": int(action.target.pattern['group']),
                "messageChain": message,
                **({"quote": action.reply.pattern['message']} if action.reply is not None else {}),
            }
        )
