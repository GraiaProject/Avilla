from __future__ import annotations

import base64
from typing import TYPE_CHECKING, cast

from avilla.core.elements import Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerialize
from avilla.onebot.resource import OneBot11ImageResource
from avilla.standard.qq.elements import Face, FlashImage

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa

OneBot11MessageSerialize = MessageSerialize[dict]


class OneBot11MessageSerializePerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @OneBot11MessageSerialize.collect(m, Text)
    async def text(self, element: Text) -> dict:
        return {"type": "text", "data": {"text": element.text}}

    @OneBot11MessageSerialize.collect(m, Face)
    async def face(self, element: Face) -> dict:
        return {"type": "face", "data": {"id": int(element.id)}}

    @OneBot11MessageSerialize.collect(m, Picture)
    async def picture(self, element: Picture) -> dict:
        return {
            "type": "image",
            "data": {
                "file": resource.file
                if isinstance(resource := element.resource, OneBot11ImageResource)
                else base64.b64encode(cast(bytes, await self.protocol.avilla.fetch_resource(element.resource))).decode(
                    "utf-8"
                )
            },
        }

    @OneBot11MessageSerialize.collect(m, FlashImage)
    async def flash_image(self, element: FlashImage):
        raw = await self.picture(element)
        raw["data"]["type"] = "flash"
        return raw

    @OneBot11MessageSerialize.collect(m, Notice)
    async def notice(self, element: Notice):
        return {"type": "at", "data": {"qq": element.target["member"]}}

    @OneBot11MessageSerialize.collect(m, NoticeAll)
    async def notice_all(self, element: NoticeAll):
        return {"type": "at", "data": {"qq": "all"}}

    # TODO
