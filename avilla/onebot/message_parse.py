from typing import TYPE_CHECKING, Any, Dict, Type

from avilla.core.elements import Image, Notice, NoticeAll, Text, Video, Audio
from avilla.core.message import Element
from avilla.core.selectors import resource as resource_selector
from avilla.core.utilles import Registrar
from avilla.core.utilles.message import AbstractMessageParser
from avilla.onebot.elements import *

if TYPE_CHECKING:
    from avilla.onebot.protocol import OnebotProtocol

registrar = Registrar()

element_map: Dict[str, Type[Element]] = {
    "text": Text,
    "reply": Reply,
    "voice": Audio,
    "video": Video,
    "face": Face,
    "rps": RPS,
    "reply": Reply,
}


@registrar.register(AbstractMessageParser)
@registrar.decorate("parsers")
class OnebotMessageParser(AbstractMessageParser):
    def type_getter(self, token: Dict[str, Any]) -> Type[Element]:
        elem_type = token.get("type", "")
        if elem_type == "at":
            if token["data"]["qq"] == "all":
                return NoticeAll
            return Notice
        elif elem_type == "image":
            if token["data"]["type"] == "flash":
                return FlashImage
            return Image
        elif elem_type in element_map:
            return element_map[elem_type]
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
    @registrar.register(FlashImage)
    async def flash_image(protocol: "OnebotProtocol", data: Dict[str, Any]) -> FlashImage:
        return FlashImage(resource_selector.image[data["data"]["url"]].provider[protocol.service.__class__])

    @staticmethod
    @registrar.register(Audio)
    async def voice(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Audio:
        return Audio(resource_selector.audio[data["data"]["url"]].provider[protocol.service.__class__])

    @staticmethod
    @registrar.register(Video)
    async def video(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Video:
        return Video(resource_selector.video[data["data"]["url"]].provider[protocol.service.__class__])

    @staticmethod
    @registrar.register(Face)
    async def face(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Face:
        return Face(data["data"]["id"])

    @staticmethod
    @registrar.register(RPS)
    async def rps(protocol: "OnebotProtocol", data: Dict[str, Any]) -> RPS:
        return RPS()

    @staticmethod
    @registrar.register(Reply)
    async def reply(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Reply:
        return Reply(data["data"]["id"])
