from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Audio, File, Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize
from avilla.core.ryanvk.endpoint import OptionalAccess
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
    Json,
    MarketFace,
    MusicShare,
    MusicShareKind,
    Poke,
    PokeKind,
    Xml,
)

if TYPE_CHECKING:
    from avilla.core.context import Context

ElizabethMessageDeserialize = MessageDeserialize[dict]


class ElizabethMessageDeserializePerform((m := ApplicationCollector())._):
    m.post_applying = True

    context: OptionalAccess[Context] = OptionalAccess()

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @ElizabethMessageDeserialize.collect(m, "Plain")
    async def text(self, raw_element: dict) -> Text:
        return Text(raw_element["text"])

    @ElizabethMessageDeserialize.collect(m, "At")
    async def at(self, raw_element: dict) -> Notice:
        if self.context:
            return Notice(self.context.scene.member(raw_element["target"]))
        return Notice(Selector().land("qq").member(raw_element["target"]))

    @ElizabethMessageDeserialize.collect(m, "AtAll")
    async def at_all(self, raw_element: dict) -> NoticeAll:
        return NoticeAll()

    @ElizabethMessageDeserialize.collect(m, "Face")
    async def face(self, raw_element: dict) -> Face:
        return Face(raw_element["faceId"], raw_element["name"])

    @ElizabethMessageDeserialize.collect(m, "MarketFace")
    async def market_face(self, raw_element: dict) -> MarketFace:
        return MarketFace(raw_element["id"], raw_element["name"])

    @ElizabethMessageDeserialize.collect(m, "Xml")
    async def xml(self, raw_element: dict) -> Xml:
        return Xml(raw_element["xml"])

    @ElizabethMessageDeserialize.collect(m, "Json")
    async def json(self, raw_element: dict) -> Json:
        return Json(raw_element["json"])

    @ElizabethMessageDeserialize.collect(m, "App")
    async def app(self, raw_element: dict) -> App:
        return App(raw_element["content"])

    @ElizabethMessageDeserialize.collect(m, "Poke")
    async def poke(self, raw_element: dict) -> Poke:
        return Poke(PokeKind(raw_element["name"]))

    @ElizabethMessageDeserialize.collect(m, "Dice")
    async def dice(self, raw_element: dict) -> Dice:
        return Dice(int(raw_element["value"]))

    @ElizabethMessageDeserialize.collect(m, "MusicShare")
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

    @ElizabethMessageDeserialize.collect(m, "File")
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

    @ElizabethMessageDeserialize.collect(m, "Image")
    async def image(self, raw_element: dict) -> Picture:
        resource = ElizabethImageResource(
            Selector().land("qq").picture(raw_element["imageId"]),
            raw_element["imageId"],
            raw_element["url"],
        )
        return Picture(resource)

    @ElizabethMessageDeserialize.collect(m, "FlashImage")
    async def flash_image(self, raw_element: dict) -> FlashImage:
        resource = ElizabethImageResource(
            Selector().land("qq").picture(raw_element["imageId"]),
            raw_element["id"],
            raw_element["url"],
        )
        return FlashImage(resource)

    @ElizabethMessageDeserialize.collect(m, "Voice")
    async def voice(self, raw_element: dict) -> Audio:
        resource = ElizabethVoiceResource(
            Selector().land("qq").voice(raw_element["voiceId"]),
            raw_element["voiceId"],
            raw_element["url"],
            raw_element["length"],
        )
        return Audio(resource)
