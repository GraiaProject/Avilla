from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core import LocalFileResource, RawResource, UrlResource
from avilla.core.builtins.resource_fetch import CoreResourceFetchPerform
from avilla.core.elements import Audio, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.telegram.elements import (
    Animation,
    Contact,
    Dice,
    Document,
    Location,
    Picture,
    Sticker,
    Venue,
    Video,
    VideoNote,
)
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import (
    MessageFragment,
    MessageFragmentAnimation,
    MessageFragmentAudio,
    MessageFragmentContact,
    MessageFragmentDice,
    MessageFragmentDocument,
    MessageFragmentLocation,
    MessageFragmentPhoto,
    MessageFragmentSticker,
    MessageFragmentText,
    MessageFragmentVenue,
    MessageFragmentVideo,
    MessageFragmentVideoNote,
)
from avilla.telegram.perform.resource_fetch import TelegramResourceFetchPerform
from avilla.telegram.resource import TelegramResource

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramMessageSerializePerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(TelegramCapability.serialize_element, element=Text)
    async def text(self, element: Text) -> MessageFragment:
        return MessageFragmentText(element.text)

    @m.entity(TelegramCapability.serialize_element, element=Picture)
    async def picture(self, element: Picture) -> MessageFragment:
        has_spoiler = getattr(element, "has_spoiler", False)
        resource = element.resource
        if isinstance(resource, TelegramResource):
            data = await TelegramResourceFetchPerform(self.account.staff).fetch_resource(resource)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentPhoto(cast(bytes, data), has_spoiler)

    @m.entity(TelegramCapability.serialize_element, element=Animation)
    async def animation(self, element: Animation) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            data = await TelegramResourceFetchPerform(self.account.staff).fetch_resource(resource)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentAnimation(cast(bytes, data), element.has_spoiler)

    @m.entity(TelegramCapability.serialize_element, element=Audio)
    async def audio(self, element: Audio) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            data = await TelegramResourceFetchPerform(self.account.staff).fetch_resource(resource)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentAudio(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Video)
    async def video(self, element: Video) -> MessageFragment:
        has_spoiler = getattr(element, "has_spoiler", False)
        resource = element.resource
        if isinstance(resource, TelegramResource):
            data = await TelegramResourceFetchPerform(self.account.staff).fetch_resource(resource)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentVideo(cast(bytes, data), has_spoiler)

    @m.entity(TelegramCapability.serialize_element, element=VideoNote)
    async def video_note(self, element: VideoNote) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            data = await TelegramResourceFetchPerform(self.account.staff).fetch_resource(resource)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentVideoNote(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Contact)
    async def contact(self, element: Contact) -> MessageFragment:
        return MessageFragmentContact(
            element.phone_number,
            element.first_name,
            element.last_name,
            element.user_id,
            element.vcard,
        )

    @m.entity(TelegramCapability.serialize_element, element=Dice)
    async def dice(self, element: Dice) -> MessageFragment:
        return MessageFragmentDice(element.emoji.value)

    @m.entity(TelegramCapability.serialize_element, element=Document)
    async def document(self, element: Document) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            data = await TelegramResourceFetchPerform(self.account.staff).fetch_resource(resource)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentDocument(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Location)
    async def location(self, element: Location) -> MessageFragment:
        return MessageFragmentLocation(element.latitude, element.longitude)

    @m.entity(TelegramCapability.serialize_element, element=Sticker)
    async def sticker(self, element: Sticker) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            data = await TelegramResourceFetchPerform(self.account.staff).fetch_resource(resource)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentSticker(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Venue)
    async def venue(self, element: Venue) -> MessageFragment:
        return MessageFragmentVenue(
            element.latitude,
            element.longitude,
            element.title,
            element.address,
        )
