from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from avilla.core.elements import Audio, Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerialize
from avilla.elizabeth.resource import ElizabethImageResource, ElizabethVoiceResource
from avilla.standard.qq.elements import (
    App,
    Dice,
    Face,
    FlashImage,
    Json,
    MusicShare,
    Poke,
    Xml,
)

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa

ElizabethMessageSerialize = MessageSerialize[dict]


class ElizabethMessageSerializePerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @ElizabethMessageSerialize.collect(m, Text)
    async def text(self, element: Text) -> dict:
        return {"type": "Plain", "text": element.text}

    @ElizabethMessageSerialize.collect(m, Notice)
    async def notice(self, element: Notice):
        return {"type": "At", "target": int(element.target.last_value)}

    @ElizabethMessageSerialize.collect(m, NoticeAll)
    async def notice_all(self, element: NoticeAll):
        return {"type": "AtAll"}

    @ElizabethMessageSerialize.collect(m, Face)
    async def face(self, element: Face) -> dict:
        return {"type": "Face", "faceId": element.id, "name": element.name}

    @ElizabethMessageSerialize.collect(m, Json)
    async def json(self, element: Json):
        return {"type": "Json", "json": element.content}

    @ElizabethMessageSerialize.collect(m, Xml)
    async def xml(self, element: Xml):
        return {"type": "Xml", "xml": element.content}

    @ElizabethMessageSerialize.collect(m, App)
    async def app(self, element: App):
        return {"type": "App", "content": element.content}

    @ElizabethMessageSerialize.collect(m, Poke)
    async def poke(self, element: Poke):
        return {"type": "Poke", "name": element.kind.value}

    @ElizabethMessageSerialize.collect(m, Dice)
    async def dice(self, element: Dice):
        return {"type": "Dice", "value": element.value}

    @ElizabethMessageSerialize.collect(m, MusicShare)
    async def music_share(self, element: MusicShare):
        return {
            "type": "MusicShare",
            "kind": element.kind.value,
            "title": element.title,
            "summary": element.content,
            "jumpUrl": element.url,
            "pictureUrl": element.thumbnail,
            "musicUrl": element.audio,
            "brief": element.brief,
        }

    @ElizabethMessageSerialize.collect(m, Picture)
    async def image(self, element: Picture) -> dict:
        if isinstance(element.resource, ElizabethImageResource):
            return {
                "type": "Image",
                "imageId": element.resource.id,
                "url": element.resource.url,
            }
        else:
            return {
                "type": "Image",
                "base64": base64.b64encode(await self.account.staff.fetch_resource(element.resource)).decode("utf-8"),
            }

    @ElizabethMessageSerialize.collect(m, FlashImage)
    async def flash_image(self, element: FlashImage):
        raw = await self.image(element)
        raw["type"] = "FlashImage"
        return raw

    @ElizabethMessageSerialize.collect(m, Audio)
    async def audio(self, element: Audio):
        if isinstance(element.resource, ElizabethVoiceResource):
            return {
                "type": "Voice",
                "voiceId": element.resource.id,
                "url": element.resource.url,
            }
        else:
            return {
                "type": "Voice",
                "base64": base64.b64encode(await self.account.staff.fetch_resource(element.resource)).decode("utf-8"),
            }
