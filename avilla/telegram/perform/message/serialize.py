from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import Element

from avilla.core import Context, LocalFileResource, RawResource, Resource, UrlResource
from avilla.core.elements import Audio, Face, File, Notice
from avilla.core.elements import Picture as CorePicture
from avilla.core.elements import Text
from avilla.core.elements import Video as CoreVideo
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.core.profile import Nick, Summary
from avilla.standard.telegram.elements import (
    Animation,
    Contact,
    Dice,
    Location,
    Picture,
    Sticker,
    Venue,
    Video,
    VideoNote,
)
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.resource import (
    TelegramAnimationResource,
    TelegramResource,
    TelegramStickerResource,
    TelegramVideoNoteResource,
    TelegramVideoResource,
    TelegramVoiceResource,
)
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramMessageSerializePerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(TelegramCapability.serialize_element, element=Text)
    async def text(self, element: Text) -> dict:
        entities = []
        if element.style:
            entities.append({"type": element.style, "offset": 0, "length": len(element.text.encode("utf-16be"))})
        return {"api_name": "sendMessage", "data": {"text": element.text, "entities": entities}}

    async def process_resource(self, element: Element, result: dict) -> dict:
        resource: Resource[bytes] = element.resource  # type: ignore

        if isinstance(resource, (TelegramResource, UrlResource)):
            data = None
            result["data"][list(result["data"].keys())[-1]] = (
                resource.url if isinstance(resource, UrlResource) else resource.file_id
            )
        elif isinstance(resource, LocalFileResource):
            data = resource.file.read_bytes()
        elif isinstance(resource, RawResource):
            data = resource.data
        else:
            data = await self.account.staff.fetch_resource(resource)

        if data is not None:
            name: str = str(id(data))  # sourcery skip: remove-unnecessary-cast
            result["data"][list(result["data"].keys())[-1]] = f"attach://{name}"
            result["file"] = {name: (name, data)}

        return result

    @m.entity(TelegramCapability.serialize_element, element=Picture)
    @m.entity(TelegramCapability.serialize_element, element=CorePicture)
    async def picture(self, element: Picture | CorePicture) -> dict:
        result = await self.process_resource(element, {"api_name": "sendPhoto", "data": {"photo": ""}})
        result["data"]["has_media_spoiler"] = int(getattr(element, "has_spoiler", False))
        return result

    @m.entity(TelegramCapability.serialize_element, element=Audio)
    async def audio(self, element: Audio) -> dict:
        resource = element.resource
        result = await self.process_resource(element, {"api_name": "sendVoice", "data": {"voice": ""}})
        if isinstance(resource, TelegramVoiceResource):
            result["data"]["duration"] = resource.duration
        return result

    @m.entity(TelegramCapability.serialize_element, element=File)
    async def document(self, element: File) -> dict:
        return await self.process_resource(element, {"api_name": "sendDocument", "data": {"document": ""}})

    @m.entity(TelegramCapability.serialize_element, element=Video)
    @m.entity(TelegramCapability.serialize_element, element=CoreVideo)
    async def video(self, element: Video) -> dict:
        resource = element.resource
        result = await self.process_resource(element, {"api_name": "sendVideo", "data": {"video": ""}})
        if isinstance(resource, TelegramVideoResource):
            result["data"]["duration"] = resource.duration
            result["data"]["width"] = resource.width
            result["data"]["height"] = resource.height
        return result

    @m.entity(TelegramCapability.serialize_element, element=Animation)
    async def animation(self, element: Animation) -> dict:
        resource = element.resource
        result = await self.process_resource(element, {"api_name": "sendAnimation", "data": {"animation": ""}})
        if isinstance(resource, TelegramAnimationResource):
            result["data"]["duration"] = resource.duration
            result["data"]["width"] = resource.width
            result["data"]["height"] = resource.height
        result["data"]["has_spoiler"] = int(getattr(element, "has_spoiler", False))
        return result

    @m.entity(TelegramCapability.serialize_element, element=VideoNote)
    async def video_note(self, element: VideoNote) -> dict:
        resource = element.resource
        result = await self.process_resource(element, {"api_name": "sendVideoNote", "data": {"video_note": ""}})
        if isinstance(resource, TelegramVideoNoteResource):
            result["data"]["duration"] = resource.duration
            result["data"]["length"] = resource.length
        return result

    @m.entity(TelegramCapability.serialize_element, element=Location)
    async def location(self, element: Location) -> dict:
        return {"api_name": "sendLocation", "data": {"latitude": element.latitude, "longitude": element.longitude}}

    @m.entity(TelegramCapability.serialize_element, element=Venue)
    async def venue(self, element: Venue) -> dict:
        return {
            "api_name": "sendVenue",
            "data": {
                "latitude": element.latitude,
                "longitude": element.longitude,
                "title": element.title,
                "address": element.address,
            },
        }

    @m.entity(TelegramCapability.serialize_element, element=Contact)
    async def contact(self, element: Contact) -> dict:
        return {
            "api_name": "sendContact",
            "data": {
                "phone_number": element.phone_number,
                "first_name": element.first_name,
                "last_name": element.last_name,
                "vcard": element.vcard,
            },
        }

    @m.entity(TelegramCapability.serialize_element, element=Dice)
    async def dice(self, element: Dice) -> dict:
        return {"api_name": "sendDice", "data": {"emoji": element.emoji}}

    @m.entity(TelegramCapability.serialize_element, element=Sticker)
    async def sticker(self, element: Sticker) -> dict:
        resource = element.resource
        result = await self.process_resource(element, {"api_name": "sendSticker", "data": {"sticker": ""}})
        if isinstance(resource, TelegramStickerResource):
            result["data"]["emoji"] = resource.emoji
        return result

    @m.entity(TelegramCapability.serialize_element, element=Notice)
    async def entity_mention(self, element: Notice) -> dict:
        cache: Memcache = self.account.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if (cached := await cache.get(f"telegram/chat({element.target.last_value})")) and "username" in cached:
            text = f"@{cached['username']}"
        else:
            text = f"@{(await self.account.staff.pull_metadata(element.target, Summary)).name}"
        entities = [{"type": "mention", "offset": 0, "length": len(text.encode("utf-16be"))}]
        return {"api_name": "sendMessage", "data": {"text": text, "entities": entities}}

    @m.entity(TelegramCapability.serialize_element, element=Face)
    async def entity_face(self, element: Face) -> dict:
        pass
