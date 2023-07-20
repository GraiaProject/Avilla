from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.access import OptionalAccess
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize
from avilla.core.selector import Selector
from avilla.red.resource import RedImageResource
from avilla.standard.qq.elements import Face

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
        return Notice(Selector().land("red").member(raw_element.get("atNtUin", "atNtUid")))

    @RedMessageDeserialize.collect(m, "face")
    async def face(self, raw_element: dict) -> Face:
        return Face(raw_element["faceIndex"], raw_element["faceText"])

    @RedMessageDeserialize.collect(m, "pic")
    async def pic(self, raw_element: dict) -> Picture:
        resource = RedImageResource(
            Selector().land("red").picture(md5 := raw_element["md5HexStr"]),
            md5,
            raw_element["fileName"],
            raw_element["sourcePath"],
        )
        return Picture(resource)
