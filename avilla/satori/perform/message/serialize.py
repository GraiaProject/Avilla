from __future__ import annotations

from flywheel import global_collect
from satori.parser import escape

from avilla.core.elements import Audio, File, Notice, NoticeAll, Picture, Text, Video
from avilla.satori.capability import SatoriCapability
from avilla.satori.element import Button
from avilla.satori.resource import SatoriResource


@global_collect
@SatoriCapability.serialize_element.impl(element=Text)
async def text(element: Text) -> str:
    text = escape(element.text)
    text.replace("\n", "<br/>")
    if not element.style:
        return text
    style = element.style
    if style in {"a", "link"}:
        return f'<a href="{text}"/>'
    if style == {
        "b",
        "strong",
        "bold",
        "i",
        "em",
        "italic",
        "u",
        "ins",
        "underline",
        "s",
        "del",
        "strike",
        "spl",
        "spoiler",
        "code",
        "sup",
        "sub",
        "superscript",
        "subscript",
        "p",
        "paragraph",
    }:
        return f"<{style}>{text}</{style}>"
    return text


@global_collect
@SatoriCapability.serialize_element.impl(element=Notice)
async def notice(element: Notice) -> str:
    if "role" in element.target.pattern:
        return f'<at role="{element.target.pattern["role"]}"/>'
    if "channel" in element.target.pattern:
        return f'<sharp id="{element.target.pattern["channel"]}"/>'
    return f'<at id="{element.target["member"]}" name="{element.display or element.target["member"]}"/>'


@global_collect
@SatoriCapability.serialize_element.impl(element=NoticeAll)
async def notice_all(element: NoticeAll) -> str:
    return '<at type="all"/>'


@global_collect
@SatoriCapability.serialize_element.impl(element=Picture)
async def picture(element: Picture) -> str:
    res = element.resource
    if not isinstance(res, SatoriResource):
        raise NotImplementedError("Only SatoriResource is supported.")
    return f'<img src="{res.src}" {"cache" if res.cache else ""}/>'


@global_collect
@SatoriCapability.serialize_element.impl(element=Audio)
async def audio(element: Audio) -> str:
    res = element.resource
    if not isinstance(res, SatoriResource):
        raise NotImplementedError("Only SatoriResource is supported.")
    return f'<audio src="{res.src}" {"cache" if res.cache else ""}/>'


@global_collect
@SatoriCapability.serialize_element.impl(element=Video)
async def video(element: Video) -> str:
    res = element.resource
    if not isinstance(res, SatoriResource):
        raise NotImplementedError("Only SatoriResource is supported.")
    return f'<video src="{res.src}" {"cache" if res.cache else ""}/>'


@global_collect
@SatoriCapability.serialize_element.impl(element=File)
async def file(element: File) -> str:
    res = element.resource
    if not isinstance(res, SatoriResource):
        raise NotImplementedError("Only SatoriResource is supported.")
    return f'<file src="{res.src}" {"cache" if res.cache else ""}/>'


@global_collect
@SatoriCapability.serialize_element.impl(element=Button)
async def button(element: Button) -> str:
    return str(element)
