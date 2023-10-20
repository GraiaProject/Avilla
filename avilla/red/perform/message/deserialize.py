from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Audio, File, Notice, NoticeAll, Picture, Text, Video, Face
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.red.capability import RedCapability
from avilla.red.resource import RedFileResource, RedImageResource, RedVideoResource, RedVoiceResource
from avilla.standard.qq.elements import App, DisplayStrategy, Forward, MarketFace, Node, Poke, PokeKind
from graia.amnesia.message import MessageChain
from graia.amnesia.message.element import Unknown
from graia.ryanvk import OptionalAccess
from selectolax.parser import HTMLParser

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.red.account import RedAccount


class RedMessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = "avilla.protocol/red::message"
    m.identify = "deserialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409
    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[RedAccount] = OptionalAccess()


    @m.entity(RedCapability.deserialize_element, element="text")
    async def text(self, element: dict) -> Text | Notice | NoticeAll:
        if not element["atType"]:
            return Text(element["content"])
        if element["atType"] == 1:
            return NoticeAll()
        if self.context:
            return Notice(
                self.context.scene.member(element.get("atNtUin", "atNtUid")),
                element["content"][1:],
            )
        return Notice(
            Selector().land("qq").member(element.get("atNtUin", "atNtUid")),
            element["content"][1:],
        )

    @m.entity(RedCapability.deserialize_element, element="face")
    async def face(self, element: dict) -> Face | Poke:
        if element["faceType"] == 5:
            return Poke(PokeKind.ChuoYiChuo)
        return Face(element["faceIndex"], element["faceText"])

    @m.entity(RedCapability.deserialize_element, element="pic")
    async def pic(self, element: dict) -> Picture:
        resource = RedImageResource(
            self.context,  # type: ignore
            Selector().land("qq").picture(md5 := element["md5HexStr"]),
            md5,
            element["fileSize"],
            element["fileName"],
            element["elementId"],
            element["fileUuid"],
            element["sourcePath"],
            element["picWidth"],
            element["picHeight"],
        )
        return Picture(resource)

    @m.entity(RedCapability.deserialize_element, element="marketFace")
    async def market_face(self, element: dict) -> MarketFace:
        return MarketFace(
            f"{element['emojiId']}/{element['key']}/{element['emojiPackageId']}",
        )

    @m.entity(RedCapability.deserialize_element, element="ark")
    async def ark(self, element: dict) -> App:
        return App(element["bytesData"])

    @m.entity(RedCapability.deserialize_element, element="file")
    async def file(self, element: dict) -> File:
        return File(
            RedFileResource(
                self.context,  # type: ignore
                Selector().land("qq").file(element["fileMd5"]),
                element["fileMd5"],
                element["fileSize"],
                element["fileName"],
                element["elementId"],
                element["fileUuid"],
            )
        )

    @m.entity(RedCapability.deserialize_element, element="ptt")
    async def ptt(self, element: dict) -> Audio:
        return Audio(
            RedVoiceResource(
                self.context,  # type: ignore
                Selector().land("qq").voice(element["md5HexStr"]),
                element["md5HexStr"],
                element.get("fileSize", 0),
                element["fileName"],
                element["elementId"],
                element["fileUuid"],
                element["filePath"],
            ),
            int(element["duration"]),
        )

    @m.entity(RedCapability.deserialize_element, element="grayTip")
    async def gray_tip(self, element: dict) -> Unknown:
        return Unknown("grayTip", element)

    @m.entity(RedCapability.deserialize_element, element="multiForwardMsg")
    async def forward(self, element: dict) -> Forward:
        root = HTMLParser(element["xmlContent"])
        title = root.css_first("source").attributes["name"]
        summary = root.css_first("summary").text()
        brief = root.css_first("msg").attributes["brief"]
        preview = [node.text() for node in root.tags("title")[1:]]
        return Forward(
            element["resId"],
            nodes=[
                Node(
                    name=(part := content.split(":", 1))[0],
                    content=MessageChain([Text(part[1].lstrip())])
                )
                for content in preview
            ],
            strategy=DisplayStrategy(title, brief, preview=preview, summary=summary)
        )

    @m.entity(RedCapability.deserialize_element, element="video")
    async def video(self, element: dict) -> Video:
        return Video(
            RedVideoResource(
                self.context,  # type: ignore
                Selector().land("qq").video(element["videoMd5"]),
                element["videoMd5"],
                element["fileSize"],
                element["fileName"],
                element["elementId"],
                element["fileUuid"],
                element["filePath"],
            )
        )
