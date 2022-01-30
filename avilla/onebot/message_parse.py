from typing import TYPE_CHECKING, Any, Dict, Type

from avilla.core.elements import Image, Notice, NoticeAll, Text
from avilla.core.message import Element
from avilla.core.selectors import resource as resource_selector
from avilla.core.utilles import Registrar
from avilla.core.utilles.message import AbstractMessageParser
from avilla.onebot.elements import Reply

if TYPE_CHECKING:
    from avilla.onebot.protocol import OnebotProtocol

registrar = Registrar()


@registrar.decorate("parsers")
class OnebotMessageParser(AbstractMessageParser):
    def type_getter(self, token: Dict[str, Any]) -> Type[Element]:
        elem_type = token.get("type")
        if elem_type == "text":
            return Text
        elif elem_type == "at":
            if token["data"]["qq"] == "all":
                return NoticeAll
            return Notice
        elif elem_type == "image":
            return Image
        elif elem_type == "reply":
            return Reply
        else:
            raise NotImplementedError(f"Unsupported message type: {elem_type}")

    @staticmethod
    @registrar.register(Text)
    async def text(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Text:
        return Text(data["data"]["text"])

    @staticmethod
    @registrar.register(Notice)
    async def notice(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Notice:
        return Notice(data["data"]["qq"])

    @staticmethod
    @registrar.register(NoticeAll)
    async def notice_all(protocol: "OnebotProtocol", data: Dict[str, Any]) -> NoticeAll:
        return NoticeAll()

    @staticmethod
    @registrar.register(Image)
    async def image(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Image:
        return Image(resource_selector.image[data["data"]["url"]].provider[protocol.service.__class__])

    @staticmethod
    @registrar.register(Reply)
    async def reply(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Reply:
        return Reply(data["data"]["id"])
