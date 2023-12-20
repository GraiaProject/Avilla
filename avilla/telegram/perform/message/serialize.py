from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core import LocalFileResource, RawResource, UrlResource
from avilla.core.builtins.resource_fetch import CoreResourceFetchPerform
from avilla.core.elements import Audio, Picture, Text, Video
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.telegram.elements import Contact, Dice, Location, Venue
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import (
    MessageFragment,
    MessageFragmentAudio,
    MessageFragmentContact,
    MessageFragmentDice,
    MessageFragmentLocation,
    MessageFragmentPhoto,
    MessageFragmentText,
    MessageFragmentVenue,
    MessageFragmentVideo,
)
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
        if isinstance(resource := element.resource, TelegramResource):
            return MessageFragmentPhoto(resource.file)
        if isinstance(element.resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(element.resource)
        elif isinstance(element.resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(element.resource)
        elif isinstance(element.resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(element.resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentPhoto(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Audio)
    async def audio(self, element: Audio) -> MessageFragment:
        if isinstance(resource := element.resource, TelegramResource):
            return MessageFragmentAudio(resource.file)
        if isinstance(element.resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(element.resource)
        elif isinstance(element.resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(element.resource)
        elif isinstance(element.resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(element.resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentAudio(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Video)
    async def video(self, element: Video) -> MessageFragment:
        if isinstance(resource := element.resource, TelegramResource):
            return MessageFragmentVideo(resource.file)
        if isinstance(element.resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(element.resource)
        elif isinstance(element.resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(element.resource)
        elif isinstance(element.resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(element.resource)
        else:
            data = await self.account.staff.fetch_resource(element.resource)
        return MessageFragmentVideo(cast(bytes, data))

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

    @m.entity(TelegramCapability.serialize_element, element=Location)
    async def location(self, element: Location) -> MessageFragment:
        return MessageFragmentLocation(element.latitude, element.longitude)

    @m.entity(TelegramCapability.serialize_element, element=Venue)
    async def venue(self, element: Venue) -> MessageFragment:
        return MessageFragmentVenue(
            element.latitude,
            element.longitude,
            element.title,
            element.address,
        )
