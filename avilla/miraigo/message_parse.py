from typing import TYPE_CHECKING, Any, Dict, Type

from avilla.core.elements import Audio, Element, Notice, NoticeAll, Text
from avilla.core.selectors import resource as resource_selector
from avilla.core.utilles import Registrar
from avilla.miraigo.elements import (
    XML,
    FlashImage,
    Image,
    Json,
    Redbag,
    Reply,
    ShowImage,
    Video,
)
from avilla.onebot.message_parse import OnebotMessageParser

if TYPE_CHECKING:
    from avilla.miraigo.protocol import MiraigoProtocol

registrar = Registrar()

element_map: Dict[str, Type[Element]] = {
    "reply": Reply,
    "redbag": Redbag,
    "video": Video,
    "xml": XML,
    "json": Json,
}


@registrar.decorate("parsers")
class MiraigoMessageParser(OnebotMessageParser):
    def type_getter(self, token: Dict[str, Any]) -> Type[Element]:
        elem_type = token.get("type", "")
        if elem_type == "image":
            sub_type = token["data"].get("tyoe")
            if sub_type == "flash":
                return FlashImage
            elif sub_type == "show":
                return ShowImage
            return Image
        elif elem_type in element_map:
            return element_map[elem_type]
        else:
            return super().type_getter(token)

    @staticmethod
    @registrar.register(Image)
    async def image(protocol: "MiraigoProtocol", data: Dict[str, Any]) -> Image:
        return Image(
            resource_selector.image[data["data"]["url"]].provider[protocol.service.__class__],
            data["data"].get(["subType"]),
        )

    @staticmethod
    @registrar.register(FlashImage)
    async def flash_image(protocol: "MiraigoProtocol", data: Dict[str, Any]) -> FlashImage:
        return FlashImage(
            resource_selector.image[data["data"]["url"]].provider[protocol.service.__class__],
            data["data"].get(["subType"]),
        )

    @staticmethod
    @registrar.register(ShowImage)
    async def show_image(protocol: "MiraigoProtocol", data: Dict[str, Any]) -> ShowImage:
        return ShowImage(
            resource_selector.image[data["data"]["url"]].provider[protocol.service.__class__],
            data["data"].get(["subType"]),
        )

    @staticmethod
    @registrar.register(Reply)
    async def reply(protocol: "MiraigoProtocol", data: Dict[str, Any]) -> Reply:
        return Reply(data["data"]["id"])

    @staticmethod
    @registrar.register(Redbag)
    async def redbag(protocol: "MiraigoProtocol", data: Dict[str, Any]) -> Redbag:
        return Redbag(data["data"]["title"])

    @staticmethod
    @registrar.register(Video)
    async def video(protocol: "MiraigoProtocol", data: Dict[str, Any]) -> Video:
        return Video(
            resource_selector.video[data["data"]["url"]].provider[protocol.service.__class__],
            resource_selector.image[data["data"]["cover"]].provider[protocol.service.__class__],
        )

    @staticmethod
    @registrar.register(XML)
    async def xml(protocol: "MiraigoProtocol", data: Dict[str, Any]) -> XML:
        return XML(data["data"]["data"])

    @staticmethod
    @registrar.register(Json)
    async def json(protocol: "MiraigoProtocol", data: Dict[str, Any]) -> Json:
        return Json(data["data"]["data"])
