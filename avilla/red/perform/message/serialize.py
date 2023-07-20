from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerialize
from avilla.red.resource import RedImageResource
from avilla.standard.qq.elements import Face

if TYPE_CHECKING:
    from ...account import RedAccount  # noqa
    from ...protocol import RedProtocol  # noqa

RedMessageSerialize = MessageSerialize[dict]


class RedMessageSerializePerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @RedMessageSerialize.collect(m, Text)
    async def text(self, element: Text) -> dict:
        return {"elementType": 1, "textElement": {"content": element.text}}

    @RedMessageSerialize.collect(m, Face)
    async def face(self, element: Face) -> dict:
        return {"elementType": 6, "faceElement": {"faceIndex": element.id}}

    @RedMessageSerialize.collect(m, Notice)
    async def notice(self, element: Notice) -> dict:
        return {"elementType": 1, "textElement": {"atType": 2, "atNtUin": element.target.last_value}}

    @RedMessageSerialize.collect(m, NoticeAll)
    async def notice_all(self, element: NoticeAll) -> dict:
        return {"elementType": 1, "textElement": {"atType": 1}}

    @RedMessageSerialize.collect(m, Picture)
    async def picture(self, element: Picture) -> dict:
        if isinstance(element.resource, RedImageResource):
            return {
                "elementType": 2,
                "picElement": {
                    "md5HexStr": element.resource.id,
                    "fileName": element.resource.name,
                    "sourcePath": str(element.resource.path.absolute()),
                },
            }
        raise NotImplementedError
