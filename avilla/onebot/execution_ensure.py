from typing import TYPE_CHECKING

from avilla.core.context import ctx_relationship
from avilla.core.execution import MessageSend
from avilla.core.message import Message
from avilla.core.relationship import Relationship
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector
from avilla.core.utilles import Registrar
from avilla.core.utilles.exec import ExecutionHandler
from avilla.onebot.config import OnebotConnectionConfig
from avilla.onebot.interface import OnebotInterface
from avilla.onebot.utilles import raise_for_obresp

if TYPE_CHECKING:
    from avilla.onebot.protocol import OnebotProtocol

registrar = Registrar()


@registrar.decorate("handlers")
class OnebotExecutionHandler(ExecutionHandler["OnebotProtocol"]):
    @staticmethod
    @registrar.register(MessageSend)
    async def send_message(protocol: "OnebotProtocol", exec: MessageSend):
        rs = ctx_relationship.get()
        interface = protocol.avilla.get_interface(OnebotInterface)
        if not interface.service.get_status(rs.self).available:
            raise RuntimeError("account is not available, check your connection!")
        if isinstance(exec.target, mainline_selector):
            keypath = exec.target.keypath()
            if keypath == "group":
                message = await protocol.serialize_message(exec.message)
                if exec.reply:
                    message = [{"type": "reply", "data": {"id": exec.reply.path["_"]}}] + message
                resp = await interface.action(
                    rs.self,
                    "send_group_msg",
                    {
                        "group_id": int(exec.target.path["group"]),
                        # v12 中应该直接传，但 v11 的类型还是 number.
                        "message": message,
                    },
                )
                raise_for_obresp(resp)
                return message_selector.mainline[exec.target]._[str(resp["data"]["message_id"])]
            elif keypath == "channel.guild":
                # TODO: gocq 相关, 发频道消息
                raise NotImplementedError
            elif keypath == "friend":
                message = await protocol.serialize_message(exec.message)
                if exec.reply:
                    message = [{"type": "reply", "data": {"id": exec.reply.path["_"]}}] + message
                resp = await interface.action(
                    rs.self,
                    "send_private_msg",  # 莫名其妙，感觉这东西只是拿来 friend msg 的
                    {
                        "user_id": int(exec.target.path["friend"]),
                        # v12 中应该直接传，但 v11 的类型还是 number.
                        "message": message,
                    },
                )
                raise_for_obresp(resp)
                return message_selector.mainline[exec.target]._[str(resp["message_id"])]
            else:
                raise NotImplementedError(f"unknown mainline/entity to send: {exec.target}")
