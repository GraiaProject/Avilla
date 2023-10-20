from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import asdict

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
from satori.element import (
    Text as SatoriText,
    At,
    Sharp,
    Link,
    Image,
    Audio as SatoriAudio,
    File as SatoriFile,
    Video as SatoriVideo,
    Quote,
    Bold,
    Italic,
    Strikethrough,
    Underline,
    Spoiler,
    Code,
    Superscript,
    Subscript,
    Br,
    Paragraph
)

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

    @m.entity(SatoriCapability.deserialize_element, raw_element=SatoriText)
    async def text(self, raw_element: SatoriText) -> Text:
        return Text(raw_element.text)

    @m.entity(SatoriCapability.deserialize_element, raw_element=At)
    async def at(self, raw_element: At) -> Notice | NoticeAll:
        if raw_element.type in ("all", "here"):
            return NoticeAll()
        scene = self.context.scene if self.context else Selector().land("satori")
        if raw_element.role:
            return Notice(scene.role(raw_element.role))
        return Notice(scene.member(raw_element.id))  # type: ignore

    @m.entity(SatoriCapability.deserialize_element, raw_element=Sharp)
    async def sharp(self, raw_element: Sharp) -> Notice:
        scene = self.context.scene if self.context else Selector().land("satori")
        return Notice(scene.into(f"~.channel({raw_element.id})"))  # type: ignore

    @m.entity(SatoriCapability.deserialize_element, raw_element=Link)
    async def a(self, raw_element: Link) -> Text:
        return Text(raw_element.text, style="link")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Image)
    async def img(self, raw_element: Image) -> Picture:
        scene = self.context.scene if self.context else Selector().land("satori")
        res = SatoriImageResource(**asdict(raw_element))
        res.selector = scene.picture(raw_element.src)
        return Picture(res)

    @m.entity(SatoriCapability.deserialize_element, raw_element=SatoriVideo)
    async def video(self, raw_element: SatoriVideo) -> Video:
        scene = self.context.scene if self.context else Selector().land("satori")
        res = SatoriVideoResource(**asdict(raw_element))
        res.selector = scene.video(raw_element.src)
        return Video(res)

    @m.entity(SatoriCapability.deserialize_element, raw_element=SatoriAudio)
    async def audio(self, raw_element: SatoriAudio) -> Audio:
        scene = self.context.scene if self.context else Selector().land("satori")
        res = SatoriAudioResource(**asdict(raw_element))
        res.selector = scene.video(raw_element.src)
        return Audio(res)

    @m.entity(SatoriCapability.deserialize_element, raw_element=SatoriFile)
    async def file(self, raw_element: SatoriFile) -> File:
        scene = self.context.scene if self.context else Selector().land("satori")
        res = SatoriFileResource(**asdict(raw_element))
        res.selector = scene.video(raw_element.src)
        return File(res)

    @m.entity(SatoriCapability.deserialize_element, raw_element=Quote)
    async def quote(self, raw_element: Quote) -> Reply:
        return Reply(raw_element.id)  # type: ignore

    @m.entity(SatoriCapability.deserialize_element, raw_element=Bold)
    async def bold(self, raw_element: Bold) -> Text:
        return Text(raw_element.text, style="bold")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Italic)
    async def italic(self, raw_element: Italic) -> Text:
        return Text(raw_element.text, style="italic")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Strikethrough)
    async def strikethrough(self, raw_element: Strikethrough) -> Text:
        return Text(raw_element.text, style="strikethrough")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Underline)
    async def underline(self, raw_element: Underline) -> Text:
        return Text(raw_element.text, style="underline")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Spoiler)
    async def spoiler(self, raw_element: Spoiler) -> Text:
        return Text(raw_element.text, style="spoiler")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Code)
    async def code(self, raw_element: Code) -> Text:
        return Text(raw_element.text, style="code")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Superscript)
    async def superscript(self, raw_element: Superscript) -> Text:
        return Text(raw_element.text, style="superscript")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Subscript)
    async def subscript(self, raw_element: Subscript) -> Text:
        return Text(raw_element.text, style="subscript")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Br)
    async def br(self, raw_element: Br) -> Text:
        return Text(raw_element.text, style="br")

    @m.entity(SatoriCapability.deserialize_element, raw_element=Paragraph)
    async def paragraph(self, raw_element: Paragraph) -> Text:
        return Text(raw_element.text, style="paragraph")
