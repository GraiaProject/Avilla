from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.elements import Audio, File, Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize
from avilla.core.selector import Selector
from avilla.elizabeth.resource import (
    ElizabethFileResource,
    ElizabethImageResource,
    ElizabethVoiceResource,
)
from avilla.standard.qq.elements import (
    App,
    Dice,
    Face,
    FlashImage,
    Forward,
    Node,
    DisplayStrategy,
    Json,
    MarketFace,
    MusicShare,
    MusicShareKind,
    Poke,
    PokeKind,
    Xml,
)
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.elizabeth.account import ElizabethAccount

ElizabethMessageDeserialize = MessageDeserialize[dict]


class ElizabethMessageDeserializePerform((m := ApplicationCollector())._):
    m.post_applying = True

    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[ElizabethAccount] = OptionalAccess()

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(ElizabethMessageDeserialize, "Plain")
    async def text(self, raw_element: dict) -> Text:
        return Text(raw_element["text"])

    @m.entity(ElizabethMessageDeserialize, "At")
    async def at(self, raw_element: dict) -> Notice:
        if self.context:
            return Notice(self.context.scene.member(raw_element["target"]))
        return Notice(Selector().land("qq").member(raw_element["target"]))

    @m.entity(ElizabethMessageDeserialize, "AtAll")
    async def at_all(self, raw_element: dict) -> NoticeAll:
        return NoticeAll()

    @m.entity(ElizabethMessageDeserialize, "Face")
    async def face(self, raw_element: dict) -> Face:
        return Face(raw_element["faceId"], raw_element["name"])

    @m.entity(ElizabethMessageDeserialize, "MarketFace")
    async def market_face(self, raw_element: dict) -> MarketFace:
        return MarketFace(raw_element["id"], raw_element["name"])

    @m.entity(ElizabethMessageDeserialize, "Xml")
    async def xml(self, raw_element: dict) -> Xml:
        return Xml(raw_element["xml"])

    @m.entity(ElizabethMessageDeserialize, "Json")
    async def json(self, raw_element: dict) -> Json:
        return Json(raw_element["json"])

    @m.entity(ElizabethMessageDeserialize, "App")
    async def app(self, raw_element: dict) -> App:
        return App(raw_element["content"])

    @m.entity(ElizabethMessageDeserialize, "Poke")
    async def poke(self, raw_element: dict) -> Poke:
        return Poke(PokeKind(raw_element["name"]))

    @m.entity(ElizabethMessageDeserialize, "Dice")
    async def dice(self, raw_element: dict) -> Dice:
        return Dice(int(raw_element["value"]))

    @m.entity(ElizabethMessageDeserialize, "MusicShare")
    async def music_share(self, raw_element: dict) -> MusicShare:
        return MusicShare(
            MusicShareKind(raw_element["kind"]),
            raw_element["title"],
            raw_element["summary"],
            raw_element["jumpUrl"],
            raw_element["pictureUrl"],
            raw_element["musicUrl"],
            raw_element["brief"],
        )

    @m.entity(ElizabethMessageDeserialize, "File")
    async def file(self, raw_element: dict) -> File:
        return File(
            ElizabethFileResource(
                Selector().land("qq").file(raw_element["id"]),
                raw_element["id"],
                None,
                raw_element["name"],
                raw_element["size"],
            )
        )

    @m.entity(ElizabethMessageDeserialize, "Image")
    async def image(self, raw_element: dict) -> Picture:
        resource = ElizabethImageResource(
            Selector().land("qq").picture(raw_element["imageId"]),
            raw_element["imageId"],
            raw_element["url"],
        )
        return Picture(resource)

    @m.entity(ElizabethMessageDeserialize, "FlashImage")
    async def flash_image(self, raw_element: dict) -> FlashImage:
        resource = ElizabethImageResource(
            Selector().land("qq").picture(raw_element["imageId"]),
            raw_element["id"],
            raw_element["url"],
        )
        return FlashImage(resource)

    @m.entity(ElizabethMessageDeserialize, "Voice")
    async def voice(self, raw_element: dict) -> Audio:
        resource = ElizabethVoiceResource(
            Selector().land("qq").voice(raw_element["voiceId"]),
            raw_element["voiceId"],
            raw_element["url"],
            raw_element["length"],
        )
        return Audio(resource)

    @m.entity(ElizabethMessageDeserialize, "Forward")
    async def forward(self, raw_element: dict) -> Forward:
        elem = Forward()
        if raw_element.get("display"):
            elem.strategy = DisplayStrategy(**raw_element["display"])
        if not self.account or not self.context:
            return elem
        for node in raw_element["nodeList"]:
            elem.nodes.append(
                Node(
                    self.context.scene.message(str(node["messageId"])),
                    node["senderName"],
                    str(node["senderId"]),
                    datetime.fromtimestamp(node["time"]),
                    await self.account.staff.ext(
                        {"context": self.context}
                    ).deserialize_message(node["messageChain"])
                )
            )
        return elem
