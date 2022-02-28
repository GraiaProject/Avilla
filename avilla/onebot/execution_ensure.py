from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.context import ctx_relationship
from avilla.core.execution import MessageFetch, MessageRevoke, MessageSend, RequestAccept, RequestReject
from avilla.core.message import Message, MessageChain
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector
from avilla.core.utilles import Registrar
from avilla.core.utilles.exec import ExecutionHandler
from avilla.onebot.elements import Forward, Reply
from avilla.onebot.execution import ForwardMessageFetch
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
        if not rs or not interface.service.get_status(rs.self).available:
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
                return message_selector.mainline[exec.target]._[str(resp["data"]["message_id"])]
            else:
                raise NotImplementedError(f"unknown mainline/entity to send: {exec.target}")

    @staticmethod
    @registrar.register(MessageRevoke)
    async def revoke_message(protocol: "OnebotProtocol", exec: MessageRevoke):
        rs = ctx_relationship.get()
        interface = protocol.avilla.get_interface(OnebotInterface)
        if not rs or not interface.service.get_status(rs.self).available:
            raise RuntimeError("account is not available, check your connection!")
        resp = await interface.action(
            rs.self,
            "delete_msg",
            {
                "message_id": exec.message.path["_"],
            },
        )
        raise_for_obresp(resp)

    @staticmethod
    @registrar.register(MessageFetch)
    async def fetch_message(protocol: "OnebotProtocol", exec: MessageFetch):
        rs = ctx_relationship.get()
        interface = protocol.avilla.get_interface(OnebotInterface)
        if not rs or not interface.service.get_status(rs.self).available:
            raise RuntimeError("account is not available, check your connection!")
        resp = await interface.action(
            rs.self,
            "get_msg",
            {
                "message_id": exec.message.path["_"],
            },
        )
        raise_for_obresp(resp)

        data = resp["data"]
        if data["message_type"] == "group":
            mainline = mainline_selector.group[str(data["group_id"])]
            sender = entity_selector.mainline[mainline].member[str(data["sender"]["user_id"])]
        elif data["message_type"] == "private":
            mainline = mainline_selector.friend[str(data["user_id"])]
            sender = entity_selector.mainline[mainline].friend[str(data["sender"]["user_id"])]
        else:
            raise NotImplementedError(f"unknown message type: {data['message_type']}")
        message_chain = await protocol.parse_message(data["message"])
        received_time = datetime.fromtimestamp(data["time"])
        reply = None
        if message_chain.has(Reply):
            reply_elem = message_chain.get_first(Reply)
            reply = message_selector.mainline[mainline]._[reply_elem.id]
            message_chain.content.remove(reply_elem)
        return Message(
            id=data["message_id"],
            mainline=mainline,
            sender=sender,
            content=message_chain,
            time=received_time,
            reply=reply,
        )

    @staticmethod
    @registrar.register(ForwardMessageFetch)
    async def fetch_forward_message(protocol: "OnebotProtocol", exec: ForwardMessageFetch):
        rs = ctx_relationship.get()
        interface = protocol.avilla.get_interface(OnebotInterface)
        if not rs or not interface.service.get_status(rs.self).available:
            raise RuntimeError("account is not available, check your connection!")
        message = exec.message
        if isinstance(message, message_selector):
            message = await OnebotExecutionHandler.fetch_message(protocol, MessageFetch(message))
        if isinstance(message, Message):
            message = message.content
        if isinstance(message, MessageChain):
            message = message.get_first(Forward)
        if isinstance(message, Forward):
            message = message.id
        resp = await interface.action(
            rs.self,
            "get_forward_msg",
            {
                "message_id": message,
            },
        )
        raise_for_obresp(resp)

        result = []
        for message in resp["data"]["messages"]:
            if rs.mainline.keypath() == "group":
                sender = entity_selector.mainline[rs.mainline].member[str(message["sender"]["user_id"])]
            elif rs.mainline.keypath() == "friend":
                sender = entity_selector.mainline[rs.mainline].friend[str(message["sender"]["user_id"])]
            else:
                raise NotImplementedError(f"unknown mainline: {rs.mainline}")
            result.append(
                Message(
                    id="",
                    mainline=rs.mainline,
                    sender=sender,
                    content=await protocol.parse_message(message["content"]),
                    time=datetime.fromtimestamp(message["time"]),
                )
            )
        return result

    @staticmethod
    @registrar.register(RequestAccept)
    async def accept_request(protocol: "OnebotProtocol", exec: RequestAccept):
        rs = ctx_relationship.get()
        interface = protocol.avilla.get_interface(OnebotInterface)
        if not rs or not interface.service.get_status(rs.self).available:
            raise RuntimeError("account is not available, check your connection!")
        if exec.request.path["mainline"].keypath() == "group":
            resp = await interface.action(
                rs.self,
                "set_group_add_request",
                {"flag": exec.request.path["_"], "type": ..., "approval": True},  # TODO: add/invite
            )
        elif exec.request.path["mainline"].keypath() == "friend":
            resp = await interface.action(
                rs.self,
                "set_friend_add_request",
                {"flag": exec.request.path["_"], "approval": True, "remark": ...},  # TODO: add remark
            )
        else:
            raise NotImplementedError(f"unknown mainline: {exec.request.path['mainline']}")
        raise_for_obresp(resp)

    @staticmethod
    @registrar.register(RequestReject)
    async def reject_request(protocol: "OnebotProtocol", exec: RequestReject):
        rs = ctx_relationship.get()
        interface = protocol.avilla.get_interface(OnebotInterface)
        if not rs or not interface.service.get_status(rs.self).available:
            raise RuntimeError("account is not available, check your connection!")
        if exec.request.path["mainline"].keypath() == "group":
            resp = await interface.action(
                rs.self,
                "set_group_add_request",
                {
                    "flag": exec.request.path["_"],
                    "type": ...,  # TODO: add/invite
                    "approval": False,
                    "reason": ...,  # TODO: add reason
                },
            )
        elif exec.request.path["mainline"].keypath() == "friend":
            resp = await interface.action(
                rs.self, "set_friend_add_request", {"flag": exec.request.path["_"], "approval": False}
            )
        else:
            raise NotImplementedError(f"unknown mainline: {exec.request.path['mainline']}")
        raise_for_obresp(resp)
