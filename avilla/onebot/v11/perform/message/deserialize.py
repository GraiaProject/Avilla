from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize
from avilla.core.selector import Selector
from avilla.standard.qq.elements import Dice, Face, FlashImage, Json, Poke, Share, Xml

from ...element import Reply
from ...resource import OneBot11ImageResource

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa

OneBot11MessageDeserialize = MessageDeserialize[dict]


class OneBot11MessageDeserializePerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @OneBot11MessageDeserialize.collect(m, "text")
    async def text(self, raw_element: dict) -> Text:
        return Text(raw_element["data"]["text"])

    @OneBot11MessageDeserialize.collect(m, "face")
    async def face(self, raw_element: dict) -> Face:
        return Face(raw_element["data"]["id"])

    @OneBot11MessageDeserialize.collect(m, "image")
    async def image(self, raw_element: dict) -> Picture | FlashImage:
        data: dict = raw_element["data"]
        resource = OneBot11ImageResource(
            Selector().land(self.account.route["land"]).picture(file := data["file"]), file, data["url"]
        )
        return FlashImage(resource) if raw_element.get("type") == "flash" else Picture(resource)

    @OneBot11MessageDeserialize.collect(m, "at")
    async def at(self, raw_element: dict) -> Notice | NoticeAll:
        # FIXME: 这里是个 Selector 但这里没办法获取到...hmmm
        if raw_element["data"]["qq"] == "all":
            return NoticeAll()
        return Notice(Selector().member(raw_element["data"]["qq"]))

    @OneBot11MessageDeserialize.collect(m, "reply")
    async def reply(self, raw_element: dict):
        return Reply(raw_element["data"]["id"])

    @OneBot11MessageDeserialize.collect(m, "dice")
    async def dice(self, raw_element: dict):
        return Dice()

    @OneBot11MessageDeserialize.collect(m, "shake")
    async def shake(self, raw_element: dict):
        return Poke()

    @OneBot11MessageDeserialize.collect(m, "json")
    async def json(self, raw_element: dict):
        return Json(raw_element["data"]["content"])

    @OneBot11MessageDeserialize.collect(m, "xml")
    async def xml(self, raw_element: dict):
        return Xml(raw_element["data"]["content"])

    @OneBot11MessageDeserialize.collect(m, "share")
    async def share(self, raw_element: dict):
        return Share(
            raw_element["data"]["url"],
            raw_element["data"]["title"],
            raw_element["data"].get("content", None),
            raw_element["data"].get("image", None),
        )

    # TODO
