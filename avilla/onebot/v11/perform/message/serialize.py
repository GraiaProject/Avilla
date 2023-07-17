from __future__ import annotations

import base64
from typing import TYPE_CHECKING, cast

from avilla.core.elements import Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerialize
from avilla.onebot.v11.resource import OneBot11ImageResource
from avilla.standard.qq.elements import (
    App,
    Dice,
    Face,
    FlashImage,
    Gift,
    Json,
    MusicShare,
    Poke,
    Share,
    Xml,
)

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa
    from avilla.onebot.v11.protocol import OneBot11Protocol  # noqa

OneBot11MessageSerialize = MessageSerialize[dict]


class OneBot11MessageSerializePerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @OneBot11MessageSerialize.collect(m, Text)
    async def text(self, element: Text) -> dict:
        return {"type": "text", "data": {"text": element.text}}

    @OneBot11MessageSerialize.collect(m, Face)
    async def face(self, element: Face) -> dict:
        return {"type": "face", "data": {"id": int(element.id)}}

    @OneBot11MessageSerialize.collect(m, Picture)
    async def picture(self, element: Picture) -> dict:
        return {
            "type": "image",
            "data": {
                "file": resource.file
                if isinstance(resource := element.resource, OneBot11ImageResource)
                else "base64://"
                + base64.b64encode(cast(bytes, await self.account.staff.fetch_resource(resource))).decode("utf-8")
            },
        }

    @OneBot11MessageSerialize.collect(m, FlashImage)
    async def flash_image(self, element: FlashImage):
        raw = await self.picture(element)
        raw["data"]["type"] = "flash"
        return raw

    @OneBot11MessageSerialize.collect(m, Notice)
    async def notice(self, element: Notice):
        return {"type": "at", "data": {"qq": element.target["member"]}}

    @OneBot11MessageSerialize.collect(m, NoticeAll)
    async def notice_all(self, element: NoticeAll):
        return {"type": "at", "data": {"qq": "all"}}

    @OneBot11MessageSerialize.collect(m, Dice)
    async def dice(self, element: Dice):
        return {"type": "dice", "data": {}}

    @OneBot11MessageSerialize.collect(m, MusicShare)
    async def music_share(self, element: MusicShare):
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

    @OneBot11MessageSerialize.collect(m, Gift)
    async def gift(self, element: Gift):
        return {"type": "gift", "data": {"id": element.kind.value, "qq": element.target["member"]}}

    @OneBot11MessageSerialize.collect(m, Json)
    async def json(self, element: Json):
        return {"type": "json", "data": {"data": element.content}}

    @OneBot11MessageSerialize.collect(m, Xml)
    async def xml(self, element: Xml):
        return {"type": "xml", "data": {"data": element.content}}

    @OneBot11MessageSerialize.collect(m, App)
    async def app(self, element: App):
        return {"type": "json", "data": {"data": element.content}}

    @OneBot11MessageSerialize.collect(m, Share)
    async def share(self, element: Share):
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

    @OneBot11MessageSerialize.collect(m, Poke)
    async def poke(self, element: Poke):
        return {"type": "shake", "data": {}}

    # TODO
