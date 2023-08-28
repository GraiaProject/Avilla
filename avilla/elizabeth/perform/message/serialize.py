from __future__ import annotations

import base64
from dataclasses import asdict
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
    Forward,
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

    @m.entity(ElizabethMessageSerialize, Text)
    async def text(self, element: Text) -> dict:
        return {"type": "Plain", "text": element.text}

    @m.entity(ElizabethMessageSerialize, Notice)
    async def notice(self, element: Notice):
        return {"type": "At", "target": int(element.target.last_value)}

    @m.entity(ElizabethMessageSerialize, NoticeAll)
    async def notice_all(self, element: NoticeAll):
        return {"type": "AtAll"}

    @m.entity(ElizabethMessageSerialize, Face)
    async def face(self, element: Face) -> dict:
        return {"type": "Face", "faceId": element.id, "name": element.name}

    @m.entity(ElizabethMessageSerialize, Json)
    async def json(self, element: Json):
        return {"type": "Json", "json": element.content}

    @m.entity(ElizabethMessageSerialize, Xml)
    async def xml(self, element: Xml):
        return {"type": "Xml", "xml": element.content}

    @m.entity(ElizabethMessageSerialize, App)
    async def app(self, element: App):
        return {"type": "App", "content": element.content}

    @m.entity(ElizabethMessageSerialize, Poke)
    async def poke(self, element: Poke):
        return {"type": "Poke", "name": element.kind.value}

    @m.entity(ElizabethMessageSerialize, Dice)
    async def dice(self, element: Dice):
        return {"type": "Dice", "value": element.value}

    @m.entity(ElizabethMessageSerialize, MusicShare)
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

    @m.entity(ElizabethMessageSerialize, Picture)
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

    @m.entity(ElizabethMessageSerialize, FlashImage)
    async def flash_image(self, element: FlashImage):
        raw = await self.image(element)
        raw["type"] = "FlashImage"
        return raw

    @m.entity(ElizabethMessageSerialize, Audio)
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

    @m.entity(ElizabethMessageSerialize, Forward)
    async def forward(self, element: Forward):
        display = asdict(element.strategy) if element.strategy else None
        nodes = []
        for node in element.nodes:
            if node.mid:
                nodes.append({"messageId": int(node.mid["message"])})
            else:
                nodes.append(
                    {
                        "senderId": int(node.uid) if node.uid else None,
                        "senderName": node.name,
                        "time": int(node.time.timestamp()),
                        "messageChain":  await self.account.staff.serialize_message(node.content)  # type: ignore
                    }
                )
        return {"type": "Forward", "display": display, "nodes": nodes}
