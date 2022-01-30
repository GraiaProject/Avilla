import fnmatch
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

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
    async def message(protocol: "OnebotProtocol", data: Dict) -> MessageReceived:
        mainline = mainline_selector.group[str(data["group_id"])]
        message_chain = await protocol.parse_message(data["message"])
        current_account = entity_selector.account[str(data["self_id"])]
        received_time = datetime.fromtimestamp(data["time"])
        reply = None
        if message_chain.has(Reply):
            reply_elem = message_chain.get_first(Reply)
            reply = message_selector.mainline[mainline]._[reply_elem.id]
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
