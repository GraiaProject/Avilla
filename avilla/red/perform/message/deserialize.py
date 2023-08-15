from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Audio, File, Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize
from avilla.core.selector import Selector
from avilla.red.resource import RedFileResource, RedImageResource, RedVoiceResource
from avilla.standard.qq.elements import App, Face, MarketFace, Poke, PokeKind
from graia.amnesia.message.element import Unknown
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context

RedMessageDeserialize = MessageDeserialize[dict]


class RedMessageDeserializePerform((m := ApplicationCollector())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409
    context: OptionalAccess[Context] = OptionalAccess()

    @RedMessageDeserialize.collect(m, "text")
    async def text(self, raw_element: dict) -> Text | Notice | NoticeAll:
        if not raw_element["atType"]:
            return Text(raw_element["content"])
        if raw_element["atType"] == 1:
            return NoticeAll()
        if self.context:
            return Notice(self.context.scene.member(raw_element.get("atNtUin", "atNtUid")))
        return Notice(Selector().land("qq").member(raw_element.get("atNtUin", "atNtUid")))

    @RedMessageDeserialize.collect(m, "face")
    async def face(self, raw_element: dict) -> Face | Poke:
        if raw_element["faceType"] == 5:
            return Poke(PokeKind.ChuoYiChuo)
        return Face(raw_element["faceIndex"], raw_element["faceText"])

    @RedMessageDeserialize.collect(m, "pic")
    async def pic(self, raw_element: dict) -> Picture:
        resource = RedImageResource(
            Selector().land("qq").picture(md5 := raw_element["md5HexStr"]),
            md5,
            raw_element["fileSize"],
            raw_element["fileName"],
            raw_element["elementId"],
            raw_element["fileUuid"],
            raw_element["sourcePath"],
            raw_element["picWidth"],
            raw_element["picHeight"],
        )
        return Picture(resource)

    @RedMessageDeserialize.collect(m, "marketFace")
    async def market_face(self, raw_element: dict) -> MarketFace:
        return MarketFace(
            f"{raw_element['emojiId']}/{raw_element['key']}/{raw_element['emojiPackageId']}",
        )

    @RedMessageDeserialize.collect(m, "ark")
    async def ark(self, raw_element: dict) -> App:
        return App(raw_element["bytesData"])

    @RedMessageDeserialize.collect(m, "file")
    async def file(self, raw_element: dict) -> File:
        return File(
            RedFileResource(
                Selector().land("qq").file(raw_element["fileMd5"]),
                raw_element["fileMd5"],
                raw_element["fileSize"],
                raw_element["fileName"],
                raw_element["elementId"],
                raw_element["fileUuid"],
            )
        )

    @RedMessageDeserialize.collect(m, "ptt")
    async def ptt(self, raw_element: dict) -> Audio:
        return Audio(
            RedVoiceResource(
                Selector().land("qq").voice(raw_element["md5HexStr"]),
                raw_element["md5HexStr"],
                raw_element.get("fileSize", 0),
                raw_element["fileName"],
                raw_element["elementId"],
                raw_element["fileUuid"],
                raw_element["filePath"],
            )
        )

    @RedMessageDeserialize.collect(m, "grayTip")
    async def gray_tip(self, raw_element: dict) -> Unknown:
        return Unknown("grayTip", raw_element)
