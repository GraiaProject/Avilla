from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.elements import Face, Notice, NoticeAll, Picture, Reference, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.onebot.v11.resource import OneBot11ImageResource
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
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.onebot.v11.account import OneBot11Account


class OneBot11MessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = "avilla.protocol/onebot11::message"
    m.identify = "deserialize"

    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[OneBot11Account] = OptionalAccess()
    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(OneBot11Capability.deserialize_element, raw_element="text")
    async def text(self, raw_element: dict) -> Text:
        return Text(raw_element["data"]["text"])

    @m.entity(OneBot11Capability.deserialize_element, raw_element="face")
    async def face(self, raw_element: dict) -> Face:
        return Face(raw_element["data"]["id"])

    @m.entity(OneBot11Capability.deserialize_element, raw_element="image")
    async def image(self, raw_element: dict) -> Picture | FlashImage:
        data: dict = raw_element["data"]
        resource = OneBot11ImageResource(Selector().land("qq").picture(file := data["file"]), file, data["url"])
        return FlashImage(resource) if raw_element.get("type") == "flash" else Picture(resource)

    @m.entity(OneBot11Capability.deserialize_element, raw_element="at")
    async def at(self, raw_element: dict) -> Notice | NoticeAll:
        if raw_element["data"]["qq"] == "all":
            return NoticeAll()
        if self.context:
            return Notice(self.context.scene.member(raw_element["data"]["qq"]))
        return Notice(Selector().land("qq").member(raw_element["data"]["qq"]))

    @m.entity(OneBot11Capability.deserialize_element, raw_element="reply")
    async def reply(self, raw_element: dict):
        if self.context:
            return Reference(self.context.scene.message(raw_element["data"]["id"]))
        return Reference(Selector().land("qq").message(raw_element["data"]["id"]))

    @m.entity(OneBot11Capability.deserialize_element, raw_element="dice")
    async def dice(self, raw_element: dict):
        return Dice()

    @m.entity(OneBot11Capability.deserialize_element, raw_element="shake")
    async def shake(self, raw_element: dict):
        return Poke()

    @m.entity(OneBot11Capability.deserialize_element, raw_element="json")
    async def json(self, raw_element: dict):
        return Json(raw_element["data"]["content"])

    @m.entity(OneBot11Capability.deserialize_element, raw_element="xml")
    async def xml(self, raw_element: dict):
        return Xml(raw_element["data"]["content"])

    @m.entity(OneBot11Capability.deserialize_element, raw_element="share")
    async def share(self, raw_element: dict):
        return Share(
            raw_element["data"]["url"],
            raw_element["data"]["title"],
            raw_element["data"].get("content", None),
            raw_element["data"].get("image", None),
        )

    @m.entity(OneBot11Capability.deserialize_element, raw_element="forward")
    async def forward(self, raw_element: dict):
        elem = Forward(raw_element["data"]["id"])
        if not self.account:
            return elem
        result = await self.account.connection.call(
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
                content=await OneBot11Capability(self.account.staff).deserialize_chain(msg["content"]),
            )
            elem.nodes.append(node)
        return elem

    # TODO
