from typing import TYPE_CHECKING, Any, Dict, Type

from avilla.core.elements import Audio, Image, Notice, NoticeAll, Text, Video
from avilla.core.message import Element
from avilla.core.selectors import (
    resource as resource_selector,
    entity as entity_selector,
)
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


@registrar.decorate("parsers")
class OnebotMessageParser(AbstractMessageParser):
    def type_getter(self, token: Dict[str, Any]) -> Type[Element]:
        elem_type = token.get("type", "")
        if elem_type == "at":
            if token["data"]["qq"] == "all":
                return NoticeAll
            return Notice
        elif elem_type == "image":
            if token["data"].get("type") == "flash":
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
        return Image(
            resource_selector.image[data["data"]["url"]].provider[
                protocol.service.__class__
            ]
        )

    @staticmethod
    @registrar.register(FlashImage)
    async def flash_image(
        protocol: "OnebotProtocol", data: Dict[str, Any]
    ) -> FlashImage:
        return FlashImage(
            resource_selector.image[data["data"]["url"]].provider[
                protocol.service.__class__
            ]
        )

    @staticmethod
    @registrar.register(Audio)
    async def voice(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Audio:
        return Audio(
            resource_selector.audio[data["data"]["url"]].provider[
                protocol.service.__class__
            ]
        )

    @staticmethod
    @registrar.register(Video)
    async def video(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Video:
        return Video(
            resource_selector.video[data["data"]["url"]].provider[
                protocol.service.__class__
            ]
        )

    @staticmethod
    @registrar.register(Face)
    async def face(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Face:
        return Face(data["data"]["id"])

    @staticmethod
    @registrar.register(RPS)
    async def rps(protocol: "OnebotProtocol", data: Dict[str, Any]) -> RPS:
        return RPS()

    @staticmethod
    @registrar.register(Dice)
    async def dice(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Dice:
        return Dice()

    @staticmethod
    @registrar.register(Shake)
    async def shake(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Shake:
        return Shake()

    @staticmethod
    @registrar.register(Poke)
    async def poke(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Poke:
        return Poke(data["data"]["type"], data["data"]["id"], data["data"]["name"])

    @staticmethod
    @registrar.register(Share)
    async def share(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Share:
        return Share(
            data["data"]["url"],
            data["data"]["title"],
            data["data"]["content"],
            data["data"]["image"],
        )

    @staticmethod
    @registrar.register(Contact)
    async def contact(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Contact:
        if data["data"]["type"] == "qq":
            return Contact(entity_selector.friend[data["data"]["id"]])
        return Contact(entity_selector.group[data["data"]["id"]])

    @staticmethod
    @registrar.register(Location)
    async def location(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Location:
        return Location(
            float(data["data"]["lat"]),
            float(data["data"]["lon"]),
            data["data"]["title"],
            data["data"]["content"],
        )

    @staticmethod
    @registrar.register(Reply)
    async def reply(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Reply:
        return Reply(data["data"]["id"])

    @staticmethod
    @registrar.register(Forward)
    async def forward(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Forward:
        return Forward(data["data"]["id"])

    @staticmethod
    @registrar.register(Node)
    async def node(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Node:
        return Node(
            None,
            data["data"]["user_id"],
            data["data"]["nickname"],
            await protocol.parse_message(data["data"]["message"]),
        )

    @staticmethod
    @registrar.register(XML)
    async def xml(protocol: "OnebotProtocol", data: Dict[str, Any]) -> XML:
        return XML(data["data"]["data"])

    @staticmethod
    @registrar.register(Json)
    async def json(protocol: "OnebotProtocol", data: Dict[str, Any]) -> Json:
        return Json(data["data"]["data"])
