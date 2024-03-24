from __future__ import annotations

from contextlib import suppress
from dataclasses import asdict

from flywheel import global_collect
from satori.element import At
from satori.element import Audio as SatoriAudio
from satori.element import Bold, Br
from satori.element import Button as SatoriButton
from satori.element import Code
from satori.element import File as SatoriFile
from satori.element import (
    Image,
    Italic,
    Link,
    Paragraph,
    Quote,
    Sharp,
    Spoiler,
    Strikethrough,
    Subscript,
    Superscript,
)
from satori.element import Text as SatoriText
from satori.element import Underline
from satori.element import Video as SatoriVideo

from avilla.core.context import Context
from avilla.core.elements import (
    Audio,
    File,
    Notice,
    NoticeAll,
    Picture,
    Reference,
    Text,
    Video,
)
from avilla.core.selector import Selector
from avilla.satori.capability import SatoriCapability
from avilla.satori.element import Button
from avilla.satori.resource import (
    SatoriAudioResource,
    SatoriFileResource,
    SatoriImageResource,
    SatoriVideoResource,
)


@global_collect
@SatoriCapability.deserialize_element.impl(element=SatoriText)
async def text(element: SatoriText) -> Text:
    return Text(element.text)


@global_collect
@SatoriCapability.deserialize_element.impl(element=At)
async def at(element: At) -> Notice | NoticeAll:
    if element.type in ("all", "here"):
        return NoticeAll()
    scene = Selector().land("satori")
    with suppress(LookupError):
        scene = Context.current.scene
    if element.role:
        return Notice(scene.role(element.role))
    return Notice(scene.member(element.id))  # type: ignore


@global_collect
@SatoriCapability.deserialize_element.impl(element=Sharp)
async def sharp(element: Sharp) -> Notice:
    scene = Selector().land("satori")
    with suppress(LookupError):
        scene = Context.current.scene
    return Notice(scene.into(f"~.channel({element.id})"))  # type: ignore


@global_collect
@SatoriCapability.deserialize_element.impl(element=Link)
async def a(element: Link) -> Text:
    return Text(element.url, style="link")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Image)
async def img(element: Image) -> Picture:
    scene = Selector().land("satori")
    with suppress(LookupError):
        scene = Context.current.scene
    res = SatoriImageResource(**asdict(element))
    res.selector = scene.picture(element.src)
    return Picture(res)


@global_collect
@SatoriCapability.deserialize_element.impl(element=SatoriVideo)
async def video(element: SatoriVideo) -> Video:
    scene = Selector().land("satori")
    with suppress(LookupError):
        scene = Context.current.scene
    res = SatoriVideoResource(**asdict(element))
    res.selector = scene.video(element.src)
    return Video(res)


@global_collect
@SatoriCapability.deserialize_element.impl(element=SatoriAudio)
async def audio(element: SatoriAudio) -> Audio:
    scene = Selector().land("satori")
    with suppress(LookupError):
        scene = Context.current.scene
    res = SatoriAudioResource(**asdict(element))
    res.selector = scene.video(element.src)
    return Audio(res)


@global_collect
@SatoriCapability.deserialize_element.impl(element=SatoriFile)
async def file(element: SatoriFile) -> File:
    scene = Selector().land("satori")
    with suppress(LookupError):
        scene = Context.current.scene
    res = SatoriFileResource(**asdict(element))
    res.selector = scene.video(element.src)
    return File(res)


@global_collect
@SatoriCapability.deserialize_element.impl(element=Quote)
async def quote(element: Quote) -> Reference:
    scene = Selector().land("satori")
    with suppress(LookupError):
        scene = Context.current.scene
    return Reference(scene.message(element.id))  # type: ignore


@global_collect
@SatoriCapability.deserialize_element.impl(element=Bold)
async def bold(element: Bold) -> Text:
    return Text(element.dumps(True), style="bold")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Italic)
async def italic(element: Italic) -> Text:
    return Text(element.dumps(True), style="italic")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Strikethrough)
async def strikethrough(element: Strikethrough) -> Text:
    return Text(element.dumps(True), style="strikethrough")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Underline)
async def underline(element: Underline) -> Text:
    return Text(element.dumps(True), style="underline")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Spoiler)
async def spoiler(element: Spoiler) -> Text:
    return Text(element.dumps(True), style="spoiler")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Code)
async def code(element: Code) -> Text:
    return Text(element.dumps(True), style="code")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Superscript)
async def superscript(element: Superscript) -> Text:
    return Text(element.dumps(True), style="superscript")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Subscript)
async def subscript(element: Subscript) -> Text:
    return Text(element.dumps(True), style="subscript")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Br)
async def br(element: Br) -> Text:
    return Text("\n", style="br")


@global_collect
@SatoriCapability.deserialize_element.impl(element=Paragraph)
async def paragraph(element: Paragraph) -> Text:
    return Text(element.dumps(True), style="paragraph")


@global_collect
@SatoriCapability.deserialize_element.impl(element=SatoriButton)
async def button(element: SatoriButton) -> Button:
    return Button(**asdict(element))
