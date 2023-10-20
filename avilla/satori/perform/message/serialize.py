from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Audio, Notice, NoticeAll, Picture, Text, Video, File
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.satori.capability import SatoriCapability
from avilla.satori.resource import SatoriResource

from satori.parser import escape

if TYPE_CHECKING:
    from avilla.satori.account import SatoriAccount  # noqa
    from avilla.satori.protocol import SatoriProtocol  # noqa


class SatoriMessageSerializePerform((m := AccountCollector["SatoriProtocol", "SatoriAccount"]())._):
    m.namespace = "avilla.protocol/satori::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(SatoriCapability.serialize_element, element=Text)
    async def text(self, element: Text) -> str:
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
            "paragraph"
        }:
            return f"<{style}>{text}</{style}>"
        return text

    @m.entity(SatoriCapability.serialize_element, element=Notice)
    async def notice(self, element: Notice) -> str:
        if "role" in element.target.pattern:
            return f'<at role="{element.target.pattern["role"]}"/>'
        if "channel" in element.target.pattern:
            return f'<sharp id="{element.target.pattern["channel"]}"/>'
        return f'<at id="{element.target["member"]}" name="{element.display or element.target["member"]}"/>'

    @m.entity(SatoriCapability.serialize_element, element=NoticeAll)
    async def notice_all(self, element: NoticeAll) -> str:
        return '<at type="all"/>'

    @m.entity(SatoriCapability.serialize_element, element=Picture)
    async def picture(self, element: Picture) -> str:
        res = element.resource
        if not isinstance(res, SatoriResource):
            raise NotImplementedError("Only SatoriResource is supported.")
        return f'<img src="{res.src}" {"cache" if res.cache else ""}/>'

    @m.entity(SatoriCapability.serialize_element, element=Audio)
    async def audio(self, element: Audio) -> str:
        res = element.resource
        if not isinstance(res, SatoriResource):
            raise NotImplementedError("Only SatoriResource is supported.")
        return f'<audio src="{res.src}" {"cache" if res.cache else ""}/>'

    @m.entity(SatoriCapability.serialize_element, element=Video)
    async def video(self, element: Video) -> str:
        res = element.resource
        if not isinstance(res, SatoriResource):
            raise NotImplementedError("Only SatoriResource is supported.")
        return f'<video src="{res.src}" {"cache" if res.cache else ""}/>'

    @m.entity(SatoriCapability.serialize_element, element=File)
    async def file(self, element: File) -> str:
        res = element.resource
        if not isinstance(res, SatoriResource):
            raise NotImplementedError("Only SatoriResource is supported.")
        return f'<file src="{res.src}" {"cache" if res.cache else ""}/>'
