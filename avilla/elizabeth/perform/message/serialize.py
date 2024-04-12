from __future__ import annotations

import base64
from dataclasses import asdict
from typing import TYPE_CHECKING

from avilla.core.elements import Audio, Face, Notice, NoticeAll, Picture, Text, Video
from avilla.core.resource import LocalFileResource, RawResource, UrlResource
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.elizabeth.capability import ElizabethCapability
from avilla.elizabeth.resource import ElizabethImageResource, ElizabethVoiceResource, ElizabethVideoResource
from avilla.standard.qq.elements import (
    App,
    Dice,
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


class ElizabethMessageSerializePerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(ElizabethCapability.serialize_element, element=Text)
    async def text(self, element: Text) -> dict:
        return {"type": "Plain", "text": element.text}

    @m.entity(ElizabethCapability.serialize_element, element=Notice)
    async def notice(self, element: Notice):
        return {"type": "At", "target": int(element.target.last_value)}

    @m.entity(ElizabethCapability.serialize_element, element=NoticeAll)
    async def notice_all(self, element: NoticeAll):
        return {"type": "AtAll"}

    @m.entity(ElizabethCapability.serialize_element, element=Face)
    async def face(self, element: Face) -> dict:
        return {"type": "Face", "faceId": element.id, "name": element.name}

    @m.entity(ElizabethCapability.serialize_element, element=Json)
    async def json(self, element: Json):
        return {"type": "Json", "json": element.content}

    @m.entity(ElizabethCapability.serialize_element, element=Xml)
    async def xml(self, element: Xml):
        return {"type": "Xml", "xml": element.content}

    @m.entity(ElizabethCapability.serialize_element, element=App)
    async def app(self, element: App):
        return {"type": "App", "content": element.content}

    @m.entity(ElizabethCapability.serialize_element, element=Poke)
    async def poke(self, element: Poke):
        return {"type": "Poke", "name": element.kind.value}

    @m.entity(ElizabethCapability.serialize_element, element=Dice)
    async def dice(self, element: Dice):
        return {"type": "Dice", "value": element.value}

    @m.entity(ElizabethCapability.serialize_element, element=MusicShare)
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

    @m.entity(ElizabethCapability.serialize_element, element=Picture)
    async def image(self, element: Picture) -> dict:
        if isinstance(element.resource, ElizabethImageResource):
            return {
                "type": "Image",
                "imageId": element.resource.id,
                "url": element.resource.url,
            }
        elif isinstance(element.resource, UrlResource):
            return {
                "type": "Image",
                "url": element.resource.url,
            }
        elif isinstance(element.resource, LocalFileResource):
            return {"type": "Image", "base64": base64.b64encode(element.resource.file.read_bytes()).decode("utf-8")}
        elif isinstance(element.resource, RawResource):
            return {"type": "Image", "base64": base64.b64encode(element.resource.data).decode("utf-8")}
        else:
            return {
                "type": "Image",
                "base64": base64.b64encode(await self.account.staff.fetch_resource(element.resource)).decode("utf-8"),
            }

    @m.entity(ElizabethCapability.serialize_element, element=FlashImage)
    async def flash_image(self, element: FlashImage):
        raw = await self.image(element)
        raw["type"] = "FlashImage"
        return raw

    @m.entity(ElizabethCapability.serialize_element, element=Audio)
    async def audio(self, element: Audio):
        if isinstance(element.resource, ElizabethVoiceResource):
            return {
                "type": "Voice",
                "voiceId": element.resource.id,
                "url": element.resource.url,
            }
        elif isinstance(element.resource, UrlResource):
            return {
                "type": "Voice",
                "url": element.resource.url,
            }
        elif isinstance(element.resource, LocalFileResource):
            return {"type": "Voice", "base64": base64.b64encode(element.resource.file.read_bytes()).decode("utf-8")}
        elif isinstance(element.resource, RawResource):
            return {"type": "Voice", "base64": base64.b64encode(element.resource.data).decode("utf-8")}
        else:
            return {
                "type": "Voice",
                "base64": base64.b64encode(await self.account.staff.fetch_resource(element.resource)).decode("utf-8"),
            }

    @m.entity(ElizabethCapability.serialize_element, element=Video)
    async def video(self, element: Video):
        if isinstance(element.resource, ElizabethVideoResource):
            return {
                "type": "ShortVideo",
                "videoId": element.resource.id,
                "videoUrl": element.resource.url,
            }
        elif isinstance(element.resource, UrlResource):
            return {
                "type": "ShortVideo",
                "videoUrl": element.resource.url,
            }
        raise NotImplementedError
        # elif isinstance(element.resource, LocalFileResource):
        #     return {"type": "Voice", "base64": base64.b64encode(element.resource.file.read_bytes()).decode("utf-8")}
        # elif isinstance(element.resource, RawResource):
        #     return {"type": "Voice", "base64": base64.b64encode(element.resource.data).decode("utf-8")}
        # else:
        #     return {
        #         "type": "Voice",
        #         "base64": base64.b64encode(await self.account.staff.fetch_resource(element.resource)).decode("utf-8"),
        #     }

    @m.entity(ElizabethCapability.serialize_element, element=Forward)
    async def forward(self, element: Forward):
        display = asdict(element.strategy) if element.strategy else None
        nodes = []
        for node in element.nodes:
            if node.mid:
                nodes.append({"messageId": int(node.mid["message"])})
            elif node.content:
                nodes.append(
                    {
                        "senderId": int(node.uid) if node.uid else None,
                        "senderName": node.name,
                        "time": int(node.time.timestamp()),
                        "messageChain": await ElizabethCapability(self.account.staff).serialize_chain(node.content),
                    }
                )
        return {"type": "Forward", "display": display, "nodeList": nodes}
