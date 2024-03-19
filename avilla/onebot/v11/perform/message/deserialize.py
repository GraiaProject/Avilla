from __future__ import annotations

from datetime import datetime
from contextlib import suppress

from avilla.core.elements import Face, Notice, NoticeAll, Picture, Reference, Text
from avilla.core.selector import Selector
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.onebot.v11.resource import OneBot11ImageResource
from avilla.core.context import Context
from avilla.standard.qq.elements import (
    Dice,
    FlashImage,
    Forward,
    Json,
    Node,
    Poke,
    Share,
    Xml,
)
from flywheel.globals import INSTANCE_CONTEXT_VAR

from avilla.onebot.v11.account import OneBot11Account

@OneBot11Capability.deserialize_element.impl(element_type="text")
async def text(element: dict) -> Text:
    return Text(element["data"]["text"])


@OneBot11Capability.deserialize_element.impl(element_type="face")
async def face(element: dict) -> Face:
    return Face(element["data"]["id"])


@OneBot11Capability.deserialize_element.impl(element_type="image")
async def image(element: dict) -> Picture | FlashImage:
    data: dict = element["data"]
    resource = OneBot11ImageResource(Selector().land("qq").picture(file := data["file"]), file, data["url"])
    return FlashImage(resource) if element.get("type") == "flash" else Picture(resource)


@OneBot11Capability.deserialize_element.impl(element_type="at")
async def at(element: dict) -> Notice | NoticeAll:
    if element["data"]["qq"] == "all":
        return NoticeAll()
    with suppress(LookupError):
        return Notice(Context.current.scene.member(element["data"]["qq"]))
    return Notice(Selector().land("qq").member(element["data"]["qq"]))


@OneBot11Capability.deserialize_element.impl(element_type="reply")
async def reply(element: dict):
    with suppress(LookupError):
        return Reference(Context.current.scene.message(element["data"]["id"]))
    return Reference(Selector().land("qq").message(element["data"]["id"]))


@OneBot11Capability.deserialize_element.impl(element_type="dice")
async def dice(element: dict):
    return Dice()


@OneBot11Capability.deserialize_element.impl(element_type="shake")
async def shake(element: dict):
    return Poke()


@OneBot11Capability.deserialize_element.impl(element_type="json")
async def json(element: dict):
    return Json(element["data"]["content"])


@OneBot11Capability.deserialize_element.impl(element_type="xml")
async def xml(element: dict):
    return Xml(element["data"]["content"])


@OneBot11Capability.deserialize_element.impl(element_type="share")
async def share(element: dict):
    return Share(
        element["data"]["url"],
        element["data"]["title"],
        element["data"].get("content", None),
        element["data"].get("image", None),
    )


@OneBot11Capability.deserialize_element.impl(element_type="forward")
async def forward(element: dict):
    elem = Forward(element["data"]["id"])

    if OneBot11Account not in INSTANCE_CONTEXT_VAR.get().instances:
        return elem

    result = await INSTANCE_CONTEXT_VAR.get().instances[OneBot11Account].connection.call(
        "get_forward_msg",
        {
            "message_id": element["data"]["id"],
        },
    )
    if result is None:
        return elem
    for msg in result["messages"]:
        node = Node(
            name=msg["sender"]["nickname"],
            uid=str(msg["sender"]["user_id"]),
            time=datetime.fromtimestamp(msg["time"]),
            content=await OneBot11Capability.deserialize_chain(msg["content"]),
        )
        elem.nodes.append(node)
    return elem


# TODO
