from typing import Awaitable, Callable, Dict
from avilla.builtins.elements import Image, Notice, NoticeAll, PlainText, Quote, Video, Voice
from avilla.message.element import Element
from avilla.onebot.elements import (
    Anonymous,
    Dice,
    Face,
    FriendRecommend,
    GroupRecommend,
    Location,
    MergedForward,
    MergedForwardCustomNode,
    Poke,
    Rps,
    Shake,
    Share,
)
from avilla.provider import HttpGetProvider
from avilla.context import ctx_protocol

ELEMENT_TYPE_MAP: Dict[str, Callable[[Dict], Awaitable[Element]]] = {}


def register(element_type: str):
    def wrapper(func: Callable[[Dict], Awaitable[Element]]):
        ELEMENT_TYPE_MAP[element_type] = func
        return func

    return wrapper


@register("text")
async def text(x: Dict):
    return PlainText(x["text"])


@register("image")
async def image(x: Dict):
    return Image(HttpGetProvider(x["url"]))


@register("at")
async def at(x: Dict):
    if x["qq"] == "all":
        return NoticeAll()
    return Notice(str(x["qq"]))


@register("reply")
async def reply(x: Dict):
    return Quote(id=x["id"])


@register("record")
async def record(x: Dict):
    return Voice(HttpGetProvider(x["url"]))


@register("video")
async def video(x: Dict):
    return Video(HttpGetProvider(x["url"]))


@register("face")
async def face(x: Dict):
    return Face(x["id"])


@register("rps")
async def rps(x: Dict):
    return Rps()


@register("dice")
async def dice(x: Dict):
    return Dice()


@register("shake")
async def shake(x: Dict):
    return Shake()


@register("poke")
async def poke(x: Dict):
    return Poke(type=x["type"], id=x["id"], name=x["name"])


@register("anonymous")
async def anonymous(x: Dict):
    return Anonymous()


@register("share")
async def share(x: Dict):
    return Share(
        url=x["url"],
        title=x["title"],
        content=x["content"],
        image=x["image"],
    )


@register("contact")
async def contact(x: Dict):
    if x["type"] == "qq":
        return FriendRecommend(x["id"])
    return GroupRecommend(x["id"])


@register("location")
async def location(x: Dict):
    return Location(
        x["lat"],
        x["lon"],
        x["title"],
        x["content"],
    )


@register("forward")
async def forward(x: Dict):
    return MergedForward(
        x["id"],
    )


@register("node")
async def node(x: Dict):
    return MergedForwardCustomNode(
        x["user_id"], x["nickname"], await ctx_protocol.get().parse_message(x["content"])
    )
