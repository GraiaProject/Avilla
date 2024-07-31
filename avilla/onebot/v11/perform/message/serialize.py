from __future__ import annotations

import base64
from typing import TYPE_CHECKING, cast

from avilla.core.elements import (
    Audio,
    Face,
    Notice,
    NoticeAll,
    Picture,
    Reference,
    Text,
    Video,
)
from avilla.core.resource import LocalFileResource, RawResource, UrlResource
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.onebot.v11.resource import (
    OneBot11ImageResource,
    OneBot11RecordResource,
    OneBot11VideoResource,
)
from avilla.standard.qq.elements import (
    App,
    Dice,
    FlashImage,
    Gift,
    Json,
    MusicShare,
    Poke,
    Share,
    Xml,
    MarketFace,
)

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa
    from avilla.onebot.v11.protocol import OneBot11Protocol  # noqa


class OneBot11MessageSerializePerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(OneBot11Capability.serialize_element, element=Text)
    async def text(self, element: Text) -> dict:
        return {"type": "text", "data": {"text": element.text}}

    @m.entity(OneBot11Capability.serialize_element, element=Face)
    async def face(self, element: Face) -> dict:
        return {"type": "face", "data": {"id": int(element.id)}}

    @m.entity(OneBot11Capability.serialize_element, element=Picture)
    async def picture(self, element: Picture) -> dict:
        if isinstance(element.resource, OneBot11ImageResource):
            return {
                "type": "image",
                "data": {
                    "file": element.resource.file,
                    "url": element.resource.url,
                },
            }
        elif isinstance(element.resource, UrlResource):
            return {
                "type": "image",
                "data": {
                    "url": element.resource.url,
                },
            }
        elif isinstance(element.resource, LocalFileResource):
            data = base64.b64encode(element.resource.file.read_bytes()).decode("utf-8")
            return {
                "type": "image",
                "data": {
                    "file": "base64://" + data,
                },
            }
        elif isinstance(element.resource, RawResource):
            data = base64.b64encode(element.resource.data).decode("utf-8")
            return {
                "type": "image",
                "data": {
                    "file": "base64://" + data,
                },
            }
        else:
            return {
                "type": "image",
                "data": {
                    "file": "base64://"
                    + base64.b64encode(cast(bytes, await self.account.staff.fetch_resource(element.resource))).decode(
                        "utf-8"
                    ),
                },
            }

    @m.entity(OneBot11Capability.serialize_element, element=Audio)
    async def audio(self, element: Audio) -> dict:
        if isinstance(element.resource, OneBot11RecordResource):
            return {
                "type": "record",
                "data": {
                    "file": element.resource.file,
                    "url": element.resource.url,
                },
            }
        elif isinstance(element.resource, UrlResource):
            return {
                "type": "record",
                "data": {
                    "url": element.resource.url,
                },
            }
        elif isinstance(element.resource, LocalFileResource):
            data = base64.b64encode(element.resource.file.read_bytes()).decode("utf-8")
            return {
                "type": "record",
                "data": {
                    "file": "base64://" + data,
                },
            }
        elif isinstance(element.resource, RawResource):
            data = base64.b64encode(element.resource.data).decode("utf-8")
            return {
                "type": "record",
                "data": {
                    "file": "base64://" + data,
                },
            }
        else:
            return {
                "type": "record",
                "data": {
                    "file": "base64://"
                    + base64.b64encode(cast(bytes, await self.account.staff.fetch_resource(element.resource))).decode(
                        "utf-8"
                    ),
                },
            }

    @m.entity(OneBot11Capability.serialize_element, element=Video)
    async def video(self, element: Video) -> dict:
        if isinstance(element.resource, OneBot11VideoResource):
            return {
                "type": "video",
                "data": {
                    "file": element.resource.file,
                    "url": element.resource.url,
                },
            }
        elif isinstance(element.resource, UrlResource):
            return {
                "type": "video",
                "data": {
                    "url": element.resource.url,
                },
            }
        elif isinstance(element.resource, LocalFileResource):
            data = base64.b64encode(element.resource.file.read_bytes()).decode("utf-8")
            return {
                "type": "video",
                "data": {
                    "file": "base64://" + data,
                },
            }
        elif isinstance(element.resource, RawResource):
            data = base64.b64encode(element.resource.data).decode("utf-8")
            return {
                "type": "video",
                "data": {
                    "file": "base64://" + data,
                },
            }
        else:
            return {
                "type": "video",
                "data": {
                    "file": "base64://"
                    + base64.b64encode(cast(bytes, await self.account.staff.fetch_resource(element.resource))).decode(
                        "utf-8"
                    ),
                },
            }

    @m.entity(OneBot11Capability.serialize_element, element=FlashImage)
    async def flash_image(self, element: FlashImage):
        raw = await self.picture(element)
        raw["data"]["type"] = "flash"
        return raw

    @m.entity(OneBot11Capability.serialize_element, element=Notice)
    async def notice(self, element: Notice):
        return {"type": "at", "data": {"qq": element.target["member"]}}

    @m.entity(OneBot11Capability.serialize_element, element=NoticeAll)
    async def notice_all(self, element: NoticeAll):
        return {"type": "at", "data": {"qq": "all"}}

    @m.entity(OneBot11Capability.serialize_element, element=Dice)
    async def dice(self, element: Dice):
        return {"type": "dice", "data": {}}

    @m.entity(OneBot11Capability.serialize_element, element=MusicShare)
    async def music_share(self, element: MusicShare):
        raw = {
            "type": "music",
            "data": {
                "type": "custom",
                "url": element.url,
                "audio": element.audio,
                "title": element.title,
            },
        }
        if element.content:
            raw["data"]["content"] = element.content
        if element.thumbnail:
            raw["data"]["image"] = element.thumbnail
        return raw

    @m.entity(OneBot11Capability.serialize_element, element=Gift)
    async def gift(self, element: Gift):
        return {"type": "gift", "data": {"id": element.kind.value, "qq": element.target["member"]}}

    @m.entity(OneBot11Capability.serialize_element, element=Json)
    async def json(self, element: Json):
        return {"type": "json", "data": {"data": element.content}}

    @m.entity(OneBot11Capability.serialize_element, element=Xml)
    async def xml(self, element: Xml):
        return {"type": "xml", "data": {"data": element.content}}

    @m.entity(OneBot11Capability.serialize_element, element=App)
    async def app(self, element: App):
        return {"type": "json", "data": {"data": element.content}}

    @m.entity(OneBot11Capability.serialize_element, element=Share)
    async def share(self, element: Share):
        res = {
            "type": "share",
            "data": {
                "url": element.url,
                "title": element.title,
            },
        }
        if element.content:
            res["data"]["content"] = element.content
        if element.thumbnail:
            res["data"]["image"] = element.thumbnail
        return res

    @m.entity(OneBot11Capability.serialize_element, element=Poke)
    async def poke(self, element: Poke):
        return {"type": "shake", "data": {}}

    @m.entity(OneBot11Capability.serialize_element, element=Reference)
    async def reply(self, element: Reference):
        return {"type": "reply", "data": {"id": element.message["message"]}}

    @m.entity(OneBot11Capability.serialize_element, element=MarketFace)
    async def market_face(self, element: MarketFace):
        if not element.tab_id or not element.key:
            raise NotImplementedError
        return {
            "type": "mface",
            "data": {
                "emojiPackageId": int(element.tab_id),
                "emojiId": element.id,
                "key": element.key,
            }
        }

    # TODO
