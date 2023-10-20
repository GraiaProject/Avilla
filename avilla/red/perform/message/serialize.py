from __future__ import annotations

import random
from pathlib import Path
from typing import TYPE_CHECKING, Any

from avilla.core.elements import Notice, NoticeAll, Picture, Text, Face, Audio
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.red.capability import RedCapability
from avilla.standard.qq.elements import MarketFace

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedMessageSerializePerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.namespace = "avilla.protocol/red::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(RedCapability.serialize_element, element=Text)
    async def text(self, element: Text) -> dict:
        return {"elementType": 1, "textElement": {"content": element.text}}

    @m.entity(RedCapability.serialize_element, element=Face)
    async def face(self, element: Face) -> dict:
        return {"elementType": 6, "faceElement": {"faceIndex": element.id}}

    @m.entity(RedCapability.serialize_element, element=Notice)
    async def notice(self, element: Notice) -> dict:
        return {
            "elementType": 1,
            "textElement": {
                "atType": 2,
                "atNtUin": element.target.last_value,
                "content": f"@{element.display or element.target.last_value}",
            }
        }

    @m.entity(RedCapability.serialize_element, element=NoticeAll)
    async def notice_all(self, element: NoticeAll) -> dict:
        return {"elementType": 1, "textElement": {"atType": 1}}

    @m.entity(RedCapability.serialize_element, element=Picture)
    async def picture(self, element: Picture) -> dict:
        data = await self.account.staff.fetch_resource(element.resource)
        resp = await self.account.websocket_client.call_http(
            "multipart",
            "api/upload",
            {
                "file": {
                    "value": data,
                    "content_type": None,
                    "filename": "file_image",
                }
            },
        )
        file = Path(resp["ntFilePath"])
        return {
            "elementType": 2,
            "picElement": {
                "original": True,
                "md5HexStr": resp["md5"],
                "picWidth": resp["imageInfo"]["width"],
                "picHeight": resp["imageInfo"]["height"],
                "fileSize": resp["fileSize"],
                "fileName": file.name,
                "sourcePath": resp["ntFilePath"],
            },
        }

    @m.entity(RedCapability.serialize_element, element=MarketFace)
    async def market_face(self, element: MarketFace) -> dict:
        emoji_id, key, emoji_package_id = element.id.split("/")
        return {
            "elementType": 11,
            "marketFaceElement": {
                "emojiId": int(emoji_id),
                "key": key,
                "emojiPackageId": int(emoji_package_id),
            },
        }

    @m.entity(RedCapability.serialize_element, element=Audio)
    async def audio(self, element: Audio) -> dict:
        data = await self.account.staff.fetch_resource(element.resource)
        resp = await self.account.websocket_client.call_http(
            "multipart",
            "api/upload",
            {
                "file": {
                    "value": data,
                    "content_type": None,
                    "filename": "file_audio",
                }
            },
        )
        file = Path(resp["ntFilePath"])
        return {
            "elementType": 4,
            "pttElement": {
                "canConvert2Text": True,
                "md5HexStr": resp["md5"],
                "fileSize": resp["fileSize"],
                "fileName": file.name,
                "filePath": resp["ntFilePath"],
                "duration": max(1, element.duration),
                "formatType": 1,
                "voiceType": 1,
                "voiceChangeType": 0,
                "playState": 1,
                "waveAmplitudes": [99 for _ in range(17)]
            },
        }

    @m.entity(RedCapability.forward_export, element=Text)
    async def forward_text(self, element: Text) -> dict:
        return {"text": {"str": element.text}}

    @m.entity(RedCapability.forward_export, element=Notice)
    async def forward_notice(self, element: Notice) -> dict:
        return {"text": {"str": f"@{element.display or element.target.last_value}"}}

    @m.entity(RedCapability.forward_export, element=NoticeAll)
    async def forward_notice_all(self, element: NoticeAll) -> dict:
        return {"text": {"str": "@全体成员"}}

    @m.entity(RedCapability.forward_export, element=Picture)
    async def forward_picture(self, element: Picture) -> dict:
        data = await self.account.staff.fetch_resource(element.resource)
        resp = await self.account.websocket_client.call_http(
            "multipart",
            "api/upload",
            {
                "file": {
                    "value": data,
                    "content_type": None,
                    "filename": "file_image",
                }
            },
        )
        md5 = resp["md5"]
        file = Path(resp["ntFilePath"])
        pid = f"{{{md5[:8].upper()}-{md5[8:12].upper()}-{md5[12:16].upper()}-{md5[16:20].upper()}-{md5[20:].upper()}}}{file.suffix}"  # noqa: E501
        return {
            "customFace": {
                "filePath": pid,
                "fileId": random.randint(0, 65535),
                "serverIp": -1740138629,
                "serverPort": 80,
                "fileType": 1001,
                "useful": 1,
                "md5": [int(md5[i : i + 2], 16) for i in range(0, 32, 2)],
                "imageType": 1001,
                "width": resp["imageInfo"]["width"],
                "height": resp["imageInfo"]["height"],
                "size": resp["fileSize"],
                "origin": 0,
                "thumbWidth": 0,
                "thumbHeight": 0,
                "pbReserve": [2, 0],
            }
        }

    @m.entity(RedCapability.forward_export, element=Any)
    async def forward_any(self, element: Any) -> dict:
        return {"text": {"str": str(element)}}
