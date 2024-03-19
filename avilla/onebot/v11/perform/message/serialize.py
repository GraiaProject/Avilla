from __future__ import annotations

import base64
from typing import cast

from flywheel import global_collect

from avilla.core.builtins.capability import CoreCapability
from avilla.core.elements import Face, Notice, NoticeAll, Picture, Text
from avilla.core.resource import LocalFileResource, RawResource, UrlResource
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.onebot.v11.resource import OneBot11ImageResource
from avilla.standard.qq.elements import (
    App,
    Dice,
    FlashImage,
    Gift,
    Json,
    MusicShare,
    Poke,
    Share,
    Xml,
)


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Text)
async def text(element: Text) -> dict:
    return {"type": "text", "data": {"text": element.text}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Face)
async def face(element: Face) -> dict:
    return {"type": "face", "data": {"id": int(element.id)}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Picture)
async def picture(element: Picture) -> dict:
    if isinstance(element.resource, OneBot11ImageResource):
        return {
            "type": "image",
            "data": {
                "file": element.resource.file,
                "url": element.resource.url,
            },
        }
    elif isinstance(element.resource, UrlResource):
        return {
            "type": "image",
            "data": {
                "url": element.resource.url,
            },
        }
    elif isinstance(element.resource, LocalFileResource):
        data = base64.b64encode(element.resource.file.read_bytes()).decode("utf-8")
        return {
            "type": "image",
            "data": {
                "file": "base64://" + data,
            },
        }
    elif isinstance(element.resource, RawResource):
        data = base64.b64encode(element.resource.data).decode("utf-8")
        return {
            "type": "image",
            "data": {
                "file": "base64://" + data,
            },
        }
    else:
        return {
            "type": "image",
            "data": {
                "file": "base64://"
                + base64.b64encode(cast(bytes, await CoreCapability.fetch(element.resource))).decode("utf-8"),
            },
        }


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=FlashImage)
async def flash_image(element: FlashImage):
    raw = await picture(element)
    raw["data"]["type"] = "flash"
    return raw


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Notice)
async def notice(element: Notice):
    return {"type": "at", "data": {"qq": element.target["member"]}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=NoticeAll)
async def notice_all(element: NoticeAll):
    return {"type": "at", "data": {"qq": "all"}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Dice)
async def dice(element: Dice):
    return {"type": "dice", "data": {}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=MusicShare)
async def music_share(element: MusicShare):
    raw = {
        "type": "music",
        "data": {
            "type": "custom",
            "url": element.url,
            "audio": element.audio,
            "title": element.title,
        },
    }
    if element.content:
        raw["data"]["content"] = element.content
    if element.thumbnail:
        raw["data"]["image"] = element.thumbnail
    return raw


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Gift)
async def gift(element: Gift):
    return {"type": "gift", "data": {"id": element.kind.value, "qq": element.target["member"]}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Json)
async def json(element: Json):
    return {"type": "json", "data": {"data": element.content}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Xml)
async def xml(element: Xml):
    return {"type": "xml", "data": {"data": element.content}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=App)
async def app(element: App):
    return {"type": "json", "data": {"data": element.content}}


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Share)
async def share(element: Share):
    res = {
        "type": "share",
        "data": {
            "url": element.url,
            "title": element.title,
        },
    }
    if element.content:
        res["data"]["content"] = element.content
    if element.thumbnail:
        res["data"]["image"] = element.thumbnail
    return res


@global_collect
@OneBot11Capability.serialize_element.impl(element_type=Poke)
async def poke(element: Poke):
    return {"type": "shake", "data": {}}


# TODO
