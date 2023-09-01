from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.elements import Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize
from avilla.core.selector import Selector
from avilla.onebot.v11.element import Reply
from avilla.onebot.v11.resource import OneBot11ImageResource
from avilla.standard.qq.elements import Dice, Face, FlashImage, Json, Poke, Share, Xml, Forward, Node
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.onebot.v11.account import OneBot11Account

OneBot11MessageDeserialize = MessageDeserialize[dict]


class OneBot11MessageDeserializePerform((m := ApplicationCollector())._):
    m.post_applying = True

    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[OneBot11Account] = OptionalAccess()
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
        resource = OneBot11ImageResource(Selector().land("qq").picture(file := data["file"]), file, data["url"])
        return FlashImage(resource) if raw_element.get("type") == "flash" else Picture(resource)

    @OneBot11MessageDeserialize.collect(m, "at")
    async def at(self, raw_element: dict) -> Notice | NoticeAll:
        if raw_element["data"]["qq"] == "all":
            return NoticeAll()
        if self.context:
            return Notice(self.context.scene.member(raw_element["data"]["qq"]))
        return Notice(Selector().land("qq").member(raw_element["data"]["qq"]))

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

    @OneBot11MessageDeserialize.collect(m, "forward")
    async def forward(self, raw_element: dict):
        elem = Forward(raw_element["data"]["id"])
        if not self.account:
            return elem
        result = await self.account.call(
            "get_forward_msg",
            {
                "message_id": raw_element["data"]["id"],
            },
        )
        if result is None:
            return elem
        for msg in result["messages"]:
            node = Node(
                name=msg["sender"]["nickname"],
                uid=str(msg["sender"]["user_id"]),
                time=datetime.fromtimestamp(msg["time"]),
                content=(
                    await self.account.staff
                    .ext({"context": self.context})
                    .deserialize_message(msg["content"])
                )
            )
            elem.nodes.append(node)
        return elem

    # TODO
