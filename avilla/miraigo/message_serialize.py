from base64 import b64encode
from typing import TYPE_CHECKING, Union, cast

from avilla.core.message import MessageChain
from avilla.core.stream import Stream
from avilla.core.transformers import u8_string
from avilla.core.utilles import Registrar
from avilla.miraigo.elements import (
    XML,
    FlashImage,
    Image,
    Json,
    Music,
    Node,
    Poke,
    Reply,
    ShowImage,
    Video,
)
from avilla.onebot.elements import Node as OnebotNode
from avilla.onebot.message_serialize import OnebotMessageSerializer

if TYPE_CHECKING:
    from .protocol import MiraigoProtocol

registrar = Registrar()


@registrar.decorate("serializers")
class MiraigoMessageSerializer(OnebotMessageSerializer):
    registrar.register(Image)(OnebotMessageSerializer.image)
    registrar.register(FlashImage)(OnebotMessageSerializer.flash_image)

    @staticmethod
    @registrar.register(ShowImage)
    async def show_image(protocol: "MiraigoProtocol", element: ShowImage):
        avilla = protocol.avilla
        # 暂时还是 base64 吧。
        status, stream = await avilla.fetch_resource(element.source)
        if not status.available:
            raise RuntimeError(f"ShowImage resource not available: {element.source} - {status.description}")
        stream = cast(Stream[bytes], stream)
        b64 = await stream.transform(b64encode).transform(u8_string).unwrap()
        return {
            "type": "image",
            "data": {
                "file": "base64://" + b64,
                "type": "show",
            },
        }

    @staticmethod
    @registrar.register(Reply)
    async def reply(protocol: "MiraigoProtocol", element: Reply):
        return {
            "type": "reply",
            "data": {
                "id": element.id,
                "text": element.text,
                "qq": element.qq,
                "time": int(element.time.timestamp()) if element.time else None,
                "seq": element.seq,
            },
        }

    @staticmethod
    @registrar.register(Music)
    async def music(protocol: "MiraigoProtocol", element: Music):
        if element.type == "custom":
            return {
                "type": "music",
                "data": {
                    "type": "custom",
                    "subtype": element.sub_type,
                    "url": str(element.url),
                    "audio": str(element.audio),
                    "title": element.title,
                    "content": element.content,
                    "image": str(element.image),
                },
            }

        return {
            "type": "music",
            "data": {
                "type": element.type,
                "id": element.id,
            },
        }

    @staticmethod
    @registrar.register(Poke)
    async def poke(protocol: "MiraigoProtocol", element: Poke):
        return {
            "type": "poke",
            "data": {
                "qq": element.qq,
            },
        }

    @staticmethod
    @registrar.register(Node)
    @registrar.register(OnebotNode)
    async def node(protocol: "MiraigoProtocol", element: Union[Node, OnebotNode]):
        if element.id:
            return {
                "type": "node",
                "data": {
                    "id": element.id,
                },
            }
        data = {
            "type": "node",
            "data": {
                "name": element.nickname,
                "uin": element.user_id,
                "content": await protocol.serialize_message(cast(MessageChain, element.content)),
            },
        }
        if isinstance(element, Node):
            data["data"]["seq"] = element.seq
            data["data"]["time"] = int(element.time.timestamp()) if element.time else None
        return data

    @staticmethod
    @registrar.register(Video)
    async def video(protocol: "MiraigoProtocol", element: Video):
        avilla = protocol.avilla
        status, stream = await avilla.fetch_resource(element.source)
        if not status.available:
            raise RuntimeError(f"Video resource not available: {element.source} - {status.description}")
        stream = cast(Stream[bytes], stream)
        video_b64 = await stream.transform(b64encode).transform(u8_string).unwrap()
        cover_b64 = None
        if element.cover:
            status, stream = await avilla.fetch_resource(element.cover)
            if not status.available:
                raise RuntimeError(
                    f"Video cover resource not available: {element.cover} - {status.description}"
                )
            stream = cast(Stream[bytes], stream)
            cover_b64 = await stream.transform(b64encode).transform(u8_string).unwrap()
        return {
            "type": "video",
            "data": {
                "file": "base64://" + video_b64,
                "cover": "base64://" + cover_b64 if cover_b64 else None,
            },
        }

    @staticmethod
    @registrar.register(XML)
    async def xml(protocol: "MiraigoProtocol", element: XML):
        return {
            "type": "xml",
            "data": {
                "xml": element.data,
                "resid": element.resid,
            },
        }

    @staticmethod
    @registrar.register(Json)
    async def json(protocol: "MiraigoProtocol", element: Json):
        return {
            "type": "json",
            "data": {
                "json": element.data,
                "resid": element.resid,
            },
        }
