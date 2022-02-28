import fnmatch
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict

from avilla.core.event.message import MessageReceived, MessageRevoked
from avilla.core.message import Message
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import message as message_selector
from avilla.core.utilles import Registrar
from avilla.core.utilles.event import AbstractEventParser
from avilla.onebot.elements import Reply
from avilla.onebot.event_parse import OnebotEventParser, OnebotEventTypeKey

if TYPE_CHECKING:
    from avilla.miraigo.protocol import MiraigoProtocol


registrar = Registrar()


@registrar.decorate("parsers")
class MiraigoEventParser(OnebotEventParser):
    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="notify", sub="lucky_king"))
    async def notify_lucky_king(protocol: "MiraigoProtocol", data: Dict):
        # TODO
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="notify", sub="honor"))
    async def notify_honor(protocol: "MiraigoProtocol", data: Dict):
        # TODO
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="group_card"))
    async def group_card(protocol: "MiraigoProtocol", data: Dict):
        # TODO
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="notify"))
    async def title_changed(protocol: "MiraigoProtocol", data: Dict):
        # TODO
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="offline_file"))
    async def offline_file(protocol: "MiraigoProtocol", data: Dict):
        # TODO
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="client_status"))
    async def client_status(protocol: "MiraigoProtocol", data: Dict):
        # TODO
        ...

    @staticmethod
    @registrar.register(OnebotEventTypeKey(post="notice", notice="essence"))
    async def essence(protocol: "MiraigoProtocol", data: Dict):
        # TODO
        ...
