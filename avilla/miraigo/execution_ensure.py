from typing import TYPE_CHECKING

from avilla.core.context import ctx_relationship
from avilla.core.execution import MessageSend
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector
from avilla.core.utilles import Registrar
from avilla.onebot.elements import Node as OnebotNode
from avilla.onebot.execution_ensure import OnebotExecutionHandler
from avilla.onebot.interface import OnebotInterface
from avilla.onebot.utilles import raise_for_obresp

if TYPE_CHECKING:
    from avilla.miraigo.protocol import MiraigoProtocol

registrar = Registrar()


@registrar.decorate("handlers")
class MiraigoExecutionHandler(OnebotExecutionHandler):
    @staticmethod
    @registrar.register(MessageSend)
    async def send_message(protocol: "MiraigoProtocol", exec: MessageSend):
        rs = ctx_relationship.get()
        interface = protocol.avilla.get_interface(OnebotInterface)
        if not interface.service.get_status(rs.self).available:
            raise RuntimeError("account is not available, check your connection!")
        if (
            isinstance(exec.target, mainline_selector)
            and exec.target.keypath() == "group"
            and any(isinstance(e, OnebotNode) for e in exec.message.content)
        ):
            message = await protocol.serialize_message(exec.message)
            resp = await interface.action(
                rs.self,
                "send_group_forward_msg",
                {
                    "group_id": exec.target.path["group"],
                    "messages": message,
                },
            )
            raise_for_obresp(resp)
            return message_selector.mainline[exec.target]._[str(resp["data"]["message_id"])]
        return await OnebotExecutionHandler.send_message(protocol, exec)
