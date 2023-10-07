from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Audio, File, Notice, NoticeAll, Picture, Text, Video
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.satori.capability import SatoriCapability
from avilla.satori.element import Reply
from avilla.satori.resource import (
    SatoriFileResource,
    SatoriImageResource,
    SatoriVideoResource,
    SatoriAudioResource,
)
from avilla.satori.utils import Element

from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.satori.account import SatoriAccount


class SatoriMessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = "avilla.protocol/satori::message"
    m.identify = "deserialize"

    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[SatoriAccount] = OptionalAccess()

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(SatoriCapability.deserialize_element, element="text")
    async def text(self, raw_element: Element) -> Text:
        return Text(raw_element.attrs["text"])

    @m.entity(SatoriCapability.deserialize_element, element="at")
    async def at(self, raw_element: Element) -> Notice | NoticeAll:
        if raw_element.attrs.get("type") in ("all", "here"):
            return NoticeAll()
        scene = self.context.scene if self.context else Selector().land("satori")
        if "role" in raw_element.attrs:
            return Notice(scene.role(raw_element.attrs["role"]))
        return Notice(scene.member(raw_element.attrs["id"]))

    @m.entity(SatoriCapability.deserialize_element, element="sharp")
    async def sharp(self, raw_element: Element) -> Notice:
        scene = self.context.scene if self.context else Selector().land("satori")
        return Notice(scene.into(f"~.channel({raw_element.attrs['id']})"))

    @m.entity(SatoriCapability.deserialize_element, element="a")
    async def a(self, raw_element: Element) -> Text:
        return Text(raw_element.attrs["href"], style="link")

    @m.entity(SatoriCapability.deserialize_element, element="img")
    @m.entity(SatoriCapability.deserialize_element, element="image")
    async def img(self, raw_element: Element) -> Picture:
        scene = self.context.scene if self.context else Selector().land("satori")
        print(raw_element)
        return Picture(
            SatoriImageResource(
            scene.picture(raw_element.attrs["src"]),
                raw_element.attrs["src"],
                raw_element.attrs.get("width"),
                raw_element.attrs.get("height"),
            )
        )

    @m.entity(SatoriCapability.deserialize_element, element="video")
    async def video(self, raw_element: Element) -> Video:
        scene = self.context.scene if self.context else Selector().land("satori")
        return Video(
            SatoriVideoResource(
            scene.video(raw_element.attrs["src"]),
                raw_element.attrs["src"],
            )
        )

    @m.entity(SatoriCapability.deserialize_element, element="audio")
    async def audio(self, raw_element: Element) -> Audio:
        scene = self.context.scene if self.context else Selector().land("satori")
        return Audio(
            SatoriAudioResource(
            scene.audio(raw_element.attrs["src"]),
                raw_element.attrs["src"],
            )
        )

    @m.entity(SatoriCapability.deserialize_element, element="file")
    async def file(self, raw_element: Element) -> File:
        scene = self.context.scene if self.context else Selector().land("satori")
        return File(
            SatoriFileResource(
            scene.file(raw_element.attrs["src"]),
                raw_element.attrs["src"],
            )
        )

    @m.entity(SatoriCapability.deserialize_element, element="quote")
    async def quote(self, raw_element: Element) -> Reply:
        return Reply(raw_element.attrs["id"])

    @m.entity(SatoriCapability.deserialize_element, element="b")
    @m.entity(SatoriCapability.deserialize_element, element="strong")
    async def bold(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="bold")

    @m.entity(SatoriCapability.deserialize_element, element="i")
    @m.entity(SatoriCapability.deserialize_element, element="em")
    async def italic(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="italic")

    @m.entity(SatoriCapability.deserialize_element, element="u")
    @m.entity(SatoriCapability.deserialize_element, element="ins")
    async def underline(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="underline")

    @m.entity(SatoriCapability.deserialize_element, element="s")
    @m.entity(SatoriCapability.deserialize_element, element="del")
    async def strikethrough(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="strike")

    @m.entity(SatoriCapability.deserialize_element, element="spl")
    async def spoiler(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="spoiler")

    @m.entity(SatoriCapability.deserialize_element, element="code")
    async def code(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="code")

    @m.entity(SatoriCapability.deserialize_element, element="sup")
    async def superscript(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="superscript")

    @m.entity(SatoriCapability.deserialize_element, element="sub")
    async def subscript(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="subscript")

    @m.entity(SatoriCapability.deserialize_element, element="br")
    async def br(self, raw_element: Element) -> Text:
        return Text("\n", style="br")

    @m.entity(SatoriCapability.deserialize_element, element="p")
    async def p(self, raw_element: Element) -> Text:
        return Text(raw_element.children[0].attrs["text"], style="paragraph")
