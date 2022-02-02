import fnmatch
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

from avilla.core.event import ResourceAvailable
from avilla.core.event.message import MessageReceived
from avilla.core.message import Message
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector
from avilla.core.utilles import Registrar
from avilla.core.utilles.event import AbstractEventParser
from avilla.onebot.elements import Reply

if TYPE_CHECKING:
    from avilla.onebot.protocol import OnebotProtocol


@dataclass(init=True, frozen=True, unsafe_hash=True)
class OnebotEventTypeKey:
    post: str
    message: Optional[str] = None
    request: Optional[str] = None
    notice: Optional[str] = None
    meta_event: Optional[str] = None
    sub: Optional[str] = None

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, OnebotEventTypeKey):
            return False
        for key in ["post", "message", "request", "notice", "meta_event", "sub"]:
            if getattr(self, key) is None:
                continue
            if not fnmatch.fnmatch(getattr(__o, key), getattr(self, key)):
                return False
        return True


registrar = Registrar()


@registrar.decorate("parsers")
class OnebotEventParser(AbstractEventParser[OnebotEventTypeKey, "OnebotProtocol"]):
    def key(self, token: Dict) -> OnebotEventTypeKey:
        return OnebotEventTypeKey(
            post=token["post_type"],
            message=token.get("message_type"),
            request=token.get("request_type"),
            notice=token.get("notice_type"),
            meta_event=token.get("meta_event_type"),
            sub=token.get("sub_type"),
        )

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="message", message="group", sub="normal"))
    async def group_message_normal(protocol: "OnebotProtocol", data: Dict) -> MessageReceived:
        mainline = mainline_selector.group[str(data["group_id"])]
        message_chain = await protocol.parse_message(data["message"])
        current_account = entity_selector.account[str(data["self_id"])]
        received_time = datetime.fromtimestamp(data["time"])
        reply = None
        if message_chain.has(Reply):
            reply_elem = message_chain.get_first(Reply)
            reply = message_selector.mainline[mainline]._[reply_elem.id]
            message_chain.content.remove(reply_elem)
        return MessageReceived(
            Message(
                time=received_time,
                id=data["message_id"],
                mainline=mainline,
                content=message_chain,
                sender=entity_selector.mainline[mainline].member[str(data["user_id"])],
                reply=reply,
            ),
            current_account,
            received_time,
        )

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="message", message="group", sub="notice"))
    async def group_message_notice(protocol: "OnebotProtocol", data: Dict) -> MessageReceived:
        mainline = mainline_selector.group[str(data["group_id"])]
        message_chain = await protocol.parse_message(data["message"])
        current_account = entity_selector.account[str(data["self_id"])]
        received_time = datetime.fromtimestamp(data["time"])
        return MessageReceived(
            Message(
                time=received_time,
                id=data["message_id"],
                mainline=mainline,
                content=message_chain,
                sender=entity_selector.mainline[mainline],  # 当作是 "群" 发的消息吧。
            ),
            current_account,
            received_time,
        )

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="message", message="group", sub="anonymous"))
    async def group_message_anonymous(protocol: "OnebotProtocol", data: Dict) -> MessageReceived:
        mainline = mainline_selector.group[str(data["group_id"])]
        message_chain = await protocol.parse_message(data["message"])
        current_account = entity_selector.account[str(data["self_id"])]
        received_time = datetime.fromtimestamp(data["time"])
        return MessageReceived(
            Message(
                time=received_time,
                id=data["message_id"],
                mainline=mainline,
                content=message_chain,
                sender=entity_selector.mainline[mainline].anonymous[str(data["anonymous"]["id"])],
            ),
            current_account,
            received_time,
        )

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="message", message="private", sub="friend"))
    async def private_message_friend(protocol: "OnebotProtocol", data: Dict) -> MessageReceived:
        mainline = mainline_selector.friend[str(data["user_id"])]
        message_chain = await protocol.parse_message(data["message"])
        current_account = entity_selector.account[str(data["self_id"])]
        received_time = datetime.fromtimestamp(data["time"])
        reply = None
        if message_chain.has(Reply):
            reply_elem = message_chain.get_first(Reply)
            reply = message_selector.mainline[mainline]._[reply_elem.id]
            message_chain.content.remove(reply_elem)
        return MessageReceived(
            Message(
                time=received_time,
                id=data["message_id"],
                mainline=mainline,
                content=message_chain,
                sender=entity_selector.mainline[mainline].friend[str(data["user_id"])],
                reply=reply,
            ),
            current_account,
            received_time,
        )

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="message", message="private", sub="group"))
    async def private_message_group(protocol: "OnebotProtocol", data: Dict) -> MessageReceived:
        # 实际上是临时消息。。啊，但是有个问题： onebot v11 的 spec 里面没写 group_id....
        # 淦。
        if "group_id" not in data:
            raise ValueError("group_id not in data, so avilla cannot handle the temp message")
        mainline = mainline_selector.group[str(data["group_id"])].member[str(data["user_id"])]
        message_chain = await protocol.parse_message(data["message"])
        current_account = entity_selector.account[str(data["self_id"])]
        received_time = datetime.fromtimestamp(data["time"])
        reply = None
        if message_chain.has(Reply):
            reply_elem = message_chain.get_first(Reply)
            reply = message_selector.mainline[mainline]._[reply_elem.id]
            message_chain.content.remove(reply_elem)
        return MessageReceived(
            Message(
                time=received_time,
                id=data["message_id"],
                mainline=mainline,
                content=message_chain,
                sender=entity_selector.mainline[mainline].member[str(data["self_id"])],
                reply=reply,
            ),
            current_account,
            received_time,
        )

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_upload"))
    async def group_upload(protocol: "OnebotProtocol", data: Dict) -> ResourceAvailable:
        # TODO: OnebotGroupFileResourceProvider
        pass

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_admin", sub="set"))
    async def group_admin_set(protocol: "OnebotProtocol", data: Dict):
        # TODO: Permission
        pass

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_admin", sub="unset"))
    async def group_admin_unset(protocol: "OnebotProtocol", data: Dict):
        # TODO: Permission
        pass

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_decrease", sub="leave"))
    async def group_decrease_leave(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_decrease", sub="kick"))
    async def group_decrease_kick(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_decrease", sub="kick_me"))
    async def group_decrease_kick_me(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_increase", sub="approve"))
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_increase", sub="invite"))
    async def group_increase(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_ban", sub="ban"))
    async def group_ban(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_ban", sub="lift_ban"))
    async def group_unban(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="friend_add"))
    async def friend_add(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_recall"))
    async def group_recall(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="friend_recall"))
    async def friend_recall(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="notify", sub="poke"))
    async def notify_poke(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="request", notice="friend"))
    async def request_friend(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="request", notice="group", sub="add"))
    async def request_group_add(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="request", notice="group", sub="invite"))
    async def request_group_invite(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="meta_event", meta_event="lifecycle", sub="enable"))
    async def meta_event_lifecycle_enable(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="meta_event", meta_event="lifecycle", sub="disable"))
    async def meta_event_lifecycle_disable(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="meta_event", meta_event="lifecycle", sub="connect"))
    async def meta_event_lifecycle_connect(protocol: "OnebotProtocol", data: Dict):
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="meta_event", meta_event="heartbeat"))
    async def meta_event_heartbeat(protocol: "OnebotProtocol", data: Dict):
        ...
