from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Audio, File, Notice, NoticeAll, Picture, Text, Video, Emoji
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize
from avilla.core.selector import Selector
from avilla.red.resource import RedFileResource, RedImageResource, RedVoiceResource, RedVideoResource
from avilla.standard.qq.elements import App, MarketFace, Poke, PokeKind, Forward, Node, DisplayStrategy
from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Unknown
from graia.ryanvk import Access
from selectolax.parser import HTMLParser

if TYPE_CHECKING:
    from avilla.core.context import Context

RedMessageDeserialize = MessageDeserialize[dict]


class RedMessageDeserializePerform((m := ApplicationCollector())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409
    context: Access[Context] = Access()

    @RedMessageDeserialize.collect(m, "text")
    async def text(self, raw_element: dict) -> Text | Notice | NoticeAll:
        if not raw_element["atType"]:
            return Text(raw_element["content"])
        if raw_element["atType"] == 1:
            return NoticeAll()
        return Notice(self.context.scene.member(raw_element.get("atNtUin", "atNtUid")))

    @RedMessageDeserialize.collect(m, "face")
    async def face(self, raw_element: dict) -> Emoji | Poke:
        if raw_element["faceType"] == 5:
            return Poke(PokeKind.ChuoYiChuo)
        return Emoji(raw_element["faceIndex"], raw_element["faceText"])

    @RedMessageDeserialize.collect(m, "pic")
    async def pic(self, raw_element: dict) -> Picture:
        resource = RedImageResource(
            self.context,
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
                self.context,
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
                self.context,
                Selector().land("qq").voice(raw_element["md5HexStr"]),
                raw_element["md5HexStr"],
                raw_element.get("fileSize", 0),
                raw_element["fileName"],
                raw_element["elementId"],
                raw_element["fileUuid"],
                raw_element["filePath"],
            ),
            int(raw_element["duration"]),
        )

    @RedMessageDeserialize.collect(m, "grayTip")
    async def gray_tip(self, raw_element: dict) -> Unknown:
        return Unknown("grayTip", raw_element)

    @RedMessageDeserialize.collect(m, "multiForwardMsg")
    async def forward(self, raw_element: dict) -> Forward:
        root = HTMLParser(raw_element["xmlContent"])
        title = root.css_first("source").attributes["name"]
        summary = root.css_first("summary").text()
        brief = root.css_first("msg").attributes["brief"]
        preview = [node.text() for node in root.tags("title")[1:]]
        return Forward(
            raw_element["resId"],
            nodes=[
                Node(
                    name=(part := content.split(":", 1))[0],
                    content=MessageChain([Text(part[1].lstrip())])
                )
                for content in preview
            ],
            strategy=DisplayStrategy(title, brief, preview=preview, summary=summary)
        )

    @RedMessageDeserialize.collect(m, "video")
    async def video(self, raw_element: dict) -> Video:
        return Video(
            RedVideoResource(
                self.context,
                Selector().land("qq").video(raw_element["videoMd5"]),
                raw_element["videoMd5"],
                raw_element["fileSize"],
                raw_element["fileName"],
                raw_element["elementId"],
                raw_element["fileUuid"],
                raw_element["filePath"],
            )
        )
