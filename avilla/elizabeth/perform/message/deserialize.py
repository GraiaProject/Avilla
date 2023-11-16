from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.elements import Audio, Face, File, Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.elizabeth.capability import ElizabethCapability
from avilla.elizabeth.resource import (
    ElizabethFileResource,
    ElizabethImageResource,
    ElizabethVoiceResource,
)
from avilla.standard.qq.elements import (
    App,
    Dice,
    DisplayStrategy,
    FlashImage,
    Forward,
    Json,
    MarketFace,
    MusicShare,
    MusicShareKind,
    Node,
    Poke,
    PokeKind,
    Xml,
)
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.elizabeth.account import ElizabethAccount


class ElizabethMessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = "avilla.protocol/elizabeth::message"
    m.identify = "deserialize"

    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[ElizabethAccount] = OptionalAccess()

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Plain")
    async def text(self, raw_element: dict) -> Text:
        return Text(raw_element["text"])

    @m.entity(ElizabethCapability.deserialize_element, raw_element="At")
    async def at(self, raw_element: dict) -> Notice:
        if self.context:
            return Notice(self.context.scene.member(raw_element["target"]))
        return Notice(Selector().land("qq").member(raw_element["target"]))

    @m.entity(ElizabethCapability.deserialize_element, raw_element="AtAll")
    async def at_all(self, raw_element: dict) -> NoticeAll:
        return NoticeAll()

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Face")
    async def face(self, raw_element: dict) -> Face:
        return Face(raw_element["faceId"], raw_element["name"])

    @m.entity(ElizabethCapability.deserialize_element, raw_element="MarketFace")
    async def market_face(self, raw_element: dict) -> MarketFace:
        return MarketFace(raw_element["id"], raw_element["name"])

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Xml")
    async def xml(self, raw_element: dict) -> Xml:
        return Xml(raw_element["xml"])

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Json")
    async def json(self, raw_element: dict) -> Json:
        return Json(raw_element["json"])

    @m.entity(ElizabethCapability.deserialize_element, raw_element="App")
    async def app(self, raw_element: dict) -> App:
        return App(raw_element["content"])

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Poke")
    async def poke(self, raw_element: dict) -> Poke:
        return Poke(PokeKind(raw_element["name"]))

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Dice")
    async def dice(self, raw_element: dict) -> Dice:
        return Dice(int(raw_element["value"]))

    @m.entity(ElizabethCapability.deserialize_element, raw_element="MusicShare")
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

    @m.entity(ElizabethCapability.deserialize_element, raw_element="File")
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

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Image")
    async def image(self, raw_element: dict) -> Picture:
        resource = ElizabethImageResource(
            Selector().land("qq").picture(raw_element["imageId"]),
            raw_element["imageId"],
            raw_element["url"],
        )
        return Picture(resource)

    @m.entity(ElizabethCapability.deserialize_element, raw_element="FlashImage")
    async def flash_image(self, raw_element: dict) -> FlashImage:
        resource = ElizabethImageResource(
            Selector().land("qq").picture(raw_element["imageId"]),
            raw_element["id"],
            raw_element["url"],
        )
        return FlashImage(resource)

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Voice")
    async def voice(self, raw_element: dict) -> Audio:
        resource = ElizabethVoiceResource(
            Selector().land("qq").voice(raw_element["voiceId"]),
            raw_element["voiceId"],
            raw_element["url"],
        )
        return Audio(resource, int(raw_element["length"]))

    @m.entity(ElizabethCapability.deserialize_element, raw_element="Forward")
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
                    await ElizabethCapability(self.account.staff).deserialize_chain((node["messageChain"])),
                )
            )
        return elem
