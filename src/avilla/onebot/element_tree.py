from typing import Awaitable, Callable, Dict

from avilla.builtins.elements import (Image, Notice, NoticeAll, PlainText,
                                      Quote, Video, Voice)
from avilla.context import ctx_protocol
from avilla.message.element import Element
from avilla.onebot.elements import (Anonymous, Dice, Face, FriendRecommend,
                                    GroupRecommend, JsonMessage, Location,
                                    MergedForward, MergedForwardCustomNode,
                                    Poke, Rps, Shake, Share, XmlMessage)
from avilla.provider import HttpGetProvider

ELEMENT_TYPE_MAP: Dict[str, Callable[[Dict], Awaitable[Element]]] = {}


def register(element_type: str):
    def wrapper(func: Callable[[Dict], Awaitable[Element]]):
        ELEMENT_TYPE_MAP[element_type] = func
        return func

    return wrapper


@register("text")
async def text(data: Dict):
    return PlainText(data["text"])


@register("image")
async def image(data: Dict):
    return Image(HttpGetProvider(data["url"]))


@register("at")
async def at(data: Dict):
    if data["qq"] == "all":
        return NoticeAll()
    return Notice(str(data["qq"]))


@register("reply")
async def reply(data: Dict):
    return Quote(id=data["id"])


@register("record")
async def record(data: Dict):
    return Voice(HttpGetProvider(data["url"]))


@register("video")
async def video(data: Dict):
    return Video(HttpGetProvider(data["url"]))


@register("face")
async def face(data: Dict):
    return Face(data["id"])


@register("rps")
async def rps(data: Dict):
    return Rps()


@register("dice")
async def dice(data: Dict):
    return Dice()


@register("shake")
async def shake(data: Dict):
    return Shake()


@register("poke")
async def poke(data: Dict):
    return Poke(type=data["type"], id=data["id"], name=data["name"])


@register("anonymous")
async def anonymous(data: Dict):
    return Anonymous()


@register("share")
async def share(data: Dict):
    return Share(
        url=data["url"],
        title=data["title"],
        content=data["content"],
        image=data["image"],
    )


@register("contact")
async def contact(data: Dict):
    if data["type"] == "qq":
        return FriendRecommend(data["id"])
    return GroupRecommend(data["id"])


@register("location")
async def location(data: Dict):
    return Location(
        data["lat"],
        data["lon"],
        data["title"],
        data["content"],
    )


@register("forward")
async def forward(data: Dict):
    return MergedForward(
        data["id"],
    )


@register("node")
async def node(data: Dict):
    return MergedForwardCustomNode(
        data["user_id"], data["nickname"], await ctx_protocol.get().parse_message(data["content"])
    )


@register("xml")
async def xml(data: Dict):
    return XmlMessage(data["data"])


@register("json")
async def json(data: Dict):
    return JsonMessage(data["data"])
