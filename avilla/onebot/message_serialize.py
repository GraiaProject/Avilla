from base64 import b64encode
from typing import TYPE_CHECKING, cast

from avilla.core.message import MessageChain
from avilla.core.elements import Audio, Image, Notice, NoticeAll, Text, Video
from avilla.core.stream import Stream
from avilla.core.transformers import u8_string
from avilla.core.utilles import Registrar
from avilla.core.utilles.message import MessageSerializer
from avilla.onebot.elements import (
    FlashImage,
    Face,
    RPS,
    Dice,
    Shake,
    Poke,
    Anonymous,
    Share,
    Contact,
    Location,
    Music,
    Reply,
    Forward,
    Node,
    XML,
    Json,
)

if TYPE_CHECKING:
    from .protocol import OnebotProtocol

registrar = Registrar()


@registrar.decorate("serializers")  # this allow you to register into other class
class OnebotMessageSerializer(MessageSerializer["OnebotProtocol"]):
    @staticmethod
    @registrar.register(Text)
    async def text(protocol: "OnebotProtocol", element: Text):
        return {
            "type": "text",
            "data": {
                "text": element.text,
            },
        }

    @staticmethod
    @registrar.register(Notice)
    async def notice(protocol: "OnebotProtocol", element: Notice):
        return {
            "type": "at",
            "data": {
                "qq": element.target.last()[1],
            },
        }

    @staticmethod
    @registrar.register(NoticeAll)
    async def notice_all(protocol: "OnebotProtocol", element: NoticeAll):
        return {"type": "at", "data": {"qq": "all"}}

    @staticmethod
    @registrar.register(Image)
    async def image(protocol: "OnebotProtocol", element: Image):
        avilla = protocol.avilla
        # 暂时还是 base64 吧。
        status, stream = await avilla.fetch_resource(element.source)
        if not status.available:
            raise RuntimeError(
                f"Image resource not available: {element.source} - {status.description}"
            )
        stream = cast(Stream[bytes], stream)
        b64 = await stream.transform(b64encode).transform(u8_string).unwrap()
        return {
            "type": "image",
            "data": {
                "file": "base64://" + b64,
            },
        }

    @staticmethod
    @registrar.register(FlashImage)
    async def flash_image(protocol: "OnebotProtocol", element: FlashImage):
        avilla = protocol.avilla
        status, stream = await avilla.fetch_resource(element.source)
        if not status.available:
            raise RuntimeError(
                f"FlashImage resource not available: {element.source} - {status.description}"
            )
        stream = cast(Stream[bytes], stream)
        b64 = await stream.transform(b64encode).transform(u8_string).unwrap()
        return {
            "type": "image",
            "data": {
                "file": "base64://" + b64,
                "type": "flash",
            },
        }

    @staticmethod
    @registrar.register(Audio)
    async def voice(protocol: "OnebotProtocol", element: Audio):
        avilla = protocol.avilla
        status, stream = await avilla.fetch_resource(element.source)
        if not status.available:
            raise RuntimeError(
                f"Image resource not available: {element.source} - {status.description}"
            )
        stream = cast(Stream[bytes], stream)
        b64 = await stream.transform(b64encode).transform(u8_string).unwrap()
        return {
            "type": "record",
            "data": {
                "file": "base64://" + b64,
            },
        }

    @staticmethod
    @registrar.register(Video)
    async def video(protocol: "OnebotProtocol", element: Video):
        avilla = protocol.avilla
        status, stream = await avilla.fetch_resource(element.source)
        if not status.available:
            raise RuntimeError(
                f"Image resource not available: {element.source} - {status.description}"
            )
        stream = cast(Stream[bytes], stream)
        b64 = await stream.transform(b64encode).transform(u8_string).unwrap()
        return {
            "type": "video",
            "data": {
                "file": "base64://" + b64,
            },
        }

    @staticmethod
    @registrar.register(Face)
    async def face(protocol: "OnebotProtocol", element: Face):
        return {
            "type": "face",
            "data": {
                "id": element.id,
            },
        }

    @staticmethod
    @registrar.register(RPS)
    async def rps(protocol: "OnebotProtocol", element: RPS):
        return {
            "type": "rps",
            "data": {},
        }

    @staticmethod
    @registrar.register(Dice)
    async def dice(protocol: "OnebotProtocol", element: Dice):
        return {
            "type": "dice",
            "data": {},
        }

    @staticmethod
    @registrar.register(Shake)
    async def shake(protocol: "OnebotProtocol", element: Shake):
        return {
            "type": "shake",
            "data": {},
        }

    @staticmethod
    @registrar.register(Poke)
    async def poke(protocol: "OnebotProtocol", element: Poke):
        return {
            "type": "poke",
            "data": {
                "type": element.type,
                "id": element.id,
            },
        }

    @staticmethod
    @registrar.register(Anonymous)
    async def anonymous(protocol: "OnebotProtocol", element: Anonymous):
        return {
            "type": "anonymous",
            "data": {
                "ignore": int(element.ignore),
            },
        }

    @staticmethod
    @registrar.register(Share)
    async def share(protocol: "OnebotProtocol", element: Share):
        return {
            "type": "share",
            "data": {
                "url": element.url,
                "title": element.title,
                "content": element.content,
                "image": element.image,
            },
        }

    @staticmethod
    @registrar.register(Contact)
    async def contact(protocol: "OnebotProtocol", element: Contact):
        if "friend" in element.entity.path:
            return {
                "type": "contact",
                "data": {
                    "type": "qq",
                    "id": element.entity.path["friend"],
                },
            }
        elif "group" in element.entity.path:
            return {
                "type": "contact",
                "data": {
                    "type": "group",
                    "id": element.entity.path["group"],
                },
            }
        raise NotImplementedError(f"Unsupported contact entity: {element.entity}")

    @staticmethod
    @registrar.register(Location)
    async def location(protocol: "OnebotProtocol", element: Location):
        return {
            "type": "location",
            "data": {
                "lat": str(element.lat),
                "lon": str(element.lon),
                "title": element.title,
                "content": element.content,
            },
        }

    @staticmethod
    @registrar.register(Music)
    async def music(protocol: "OnebotProtocol", element: Music):
        if element.type == "custom":
            return {
                "type": "music",
                "data": {
                    "type": "custom",
                    "url": str(element.url),
                    "audio": str(element.audio),
                    "title": element.title,
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
    @registrar.register(Reply)
    async def reply(protocol: "OnebotProtocol", element: Reply):
        return {
            "type": "reply",
            "data": {
                "id": element.id,
            },
        }
    
    @staticmethod
    @registrar.register(Node)
    async def node(protocol: "OnebotProtocol", element: Node):
        if element.id:
            return {
            "type": "node",
            "data": {
                "id": element.id,
            },
        }
        return {
            "type": "node",
            "data": {
                "user_id": element.user_id,
                "nickname": element.nickname,
                "content": await protocol.serialize_message(cast(MessageChain,element.content)),
            },
        }
    
    @staticmethod
    @registrar.register(XML)
    async def xml(protocol: "OnebotProtocol", element: XML):
        return {
            "type": "xml",
            "data": {
                "data": element.data,
            },
        }
    
    @staticmethod
    @registrar.register(Json)
    async def json(protocol: "OnebotProtocol", element: Json):
        return {
            "type": "json",
            "data": {
                "data": element.data,
            },
        }