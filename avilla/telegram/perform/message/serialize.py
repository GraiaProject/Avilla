from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core import LocalFileResource, RawResource, UrlResource
from avilla.core.builtins.resource_fetch import CoreResourceFetchPerform
from avilla.core.elements import Audio, Face, File, Notice, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.telegram.constants import MessageEntityType
from avilla.standard.telegram.elements import (
    Animation,
    Contact,
    Dice,
    Entity,
    EntityBlockQuote,
    EntityBold,
    EntityBotCommand,
    EntityCashTag,
    EntityCode,
    EntityEmail,
    EntityHashTag,
    EntityItalic,
    EntityPhoneNumber,
    EntityPre,
    EntitySpoiler,
    EntityStrikeThrough,
    EntityTextLink,
    EntityUnderline,
    EntityUrl,
    Location,
    Picture,
    Reference,
    Sticker,
    Venue,
    Video,
    VideoNote,
    Voice,
)
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import (
    MessageFragment,
    MessageFragmentAnimation,
    MessageFragmentAudio,
    MessageFragmentContact,
    MessageFragmentDice,
    MessageFragmentDocument,
    MessageFragmentEntity,
    MessageFragmentLocation,
    MessageFragmentPhoto,
    MessageFragmentReference,
    MessageFragmentSticker,
    MessageFragmentText,
    MessageFragmentVenue,
    MessageFragmentVideo,
    MessageFragmentVideoNote,
    MessageFragmentVoice,
)
from avilla.telegram.resource import TelegramResource

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramMessageSerializePerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(TelegramCapability.serialize_element, element=Reference)
    async def reference(self, element: Reference) -> MessageFragment:
        return MessageFragmentReference(element.message)

    @m.entity(TelegramCapability.serialize_element, element=Text)
    async def text(self, element: Text) -> MessageFragment:
        return MessageFragmentText(element.text)

    @m.entity(TelegramCapability.serialize_element, element=Picture)
    async def picture(self, element: Picture) -> MessageFragment:
        has_spoiler = getattr(element, "has_spoiler", False)
        resource = element.resource
        if isinstance(resource, TelegramResource):
            return MessageFragmentPhoto(resource.media, has_spoiler)
        if isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(resource)
        return MessageFragmentPhoto(cast(bytes, data), has_spoiler)

    @m.entity(TelegramCapability.serialize_element, element=Audio)
    async def audio(self, element: Audio) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            return MessageFragmentAudio(resource.media)
        if isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(resource)
        return MessageFragmentAudio(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Video)
    async def video(self, element: Video) -> MessageFragment:
        has_spoiler = getattr(element, "has_spoiler", False)
        resource = element.resource
        if isinstance(resource, TelegramResource):
            return MessageFragmentVideo(resource.media, has_spoiler)
        if isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(resource)
        return MessageFragmentVideo(cast(bytes, data), has_spoiler)

    @m.entity(TelegramCapability.serialize_element, element=Animation)
    async def animation(self, element: Animation) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            return MessageFragmentAnimation(resource.media, element.has_spoiler)
        if isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(resource)
        return MessageFragmentAnimation(cast(bytes, data), element.has_spoiler)

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

    @m.entity(TelegramCapability.serialize_element, element=File)
    async def document(self, element: File) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            return MessageFragmentDocument(resource.media)
        if isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(resource)
        return MessageFragmentDocument(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Location)
    async def location(self, element: Location) -> MessageFragment:
        return MessageFragmentLocation(element.latitude, element.longitude)

    @m.entity(TelegramCapability.serialize_element, element=Sticker)
    async def sticker(self, element: Sticker) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            return MessageFragmentSticker(resource.media)
        if isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(resource)
        return MessageFragmentSticker(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Venue)
    async def venue(self, element: Venue) -> MessageFragment:
        return MessageFragmentVenue(
            element.latitude,
            element.longitude,
            element.title,
            element.address,
        )

    @m.entity(TelegramCapability.serialize_element, element=VideoNote)
    async def video_note(self, element: VideoNote) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            return MessageFragmentVideoNote(resource.media)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(resource)
        return MessageFragmentVideoNote(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=Voice)
    async def voice(self, element: Voice) -> MessageFragment:
        resource = element.resource
        if isinstance(resource, TelegramResource):
            return MessageFragmentVoice(resource.media)
        elif isinstance(resource, RawResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_raw(resource)
        elif isinstance(resource, UrlResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_url(resource)
        elif isinstance(resource, LocalFileResource):
            data = await CoreResourceFetchPerform(self.account.staff).fetch_localfile(resource)
        else:
            data = await self.account.staff.fetch_resource(resource)
        return MessageFragmentVoice(cast(bytes, data))

    @m.entity(TelegramCapability.serialize_element, element=EntityHashTag)
    @m.entity(TelegramCapability.serialize_element, element=EntityCashTag)
    @m.entity(TelegramCapability.serialize_element, element=EntityPhoneNumber)
    @m.entity(TelegramCapability.serialize_element, element=EntityBotCommand)
    @m.entity(TelegramCapability.serialize_element, element=EntityUrl)
    @m.entity(TelegramCapability.serialize_element, element=EntityEmail)
    @m.entity(TelegramCapability.serialize_element, element=EntityBold)
    @m.entity(TelegramCapability.serialize_element, element=EntityItalic)
    @m.entity(TelegramCapability.serialize_element, element=EntityCode)
    @m.entity(TelegramCapability.serialize_element, element=EntityPre)
    @m.entity(TelegramCapability.serialize_element, element=EntityTextLink)
    @m.entity(TelegramCapability.serialize_element, element=EntityUnderline)
    @m.entity(TelegramCapability.serialize_element, element=EntityStrikeThrough)
    @m.entity(TelegramCapability.serialize_element, element=EntitySpoiler)
    @m.entity(TelegramCapability.serialize_element, element=EntityBlockQuote)
    async def entity(self, element: Entity) -> MessageFragment:
        return MessageFragmentEntity(
            element.text,
            element.type,  # type: ignore
            data={k: v for k, v in element.__dict__.items() if k not in ("text", "type")},
        )

    @m.entity(TelegramCapability.serialize_element, element=Notice)
    async def entity_mention(self, element: Notice) -> MessageFragment:
        return MessageFragmentEntity(
            str(element.display or element.target.last_value), MessageEntityType.MENTION, data={}
        )

    @m.entity(TelegramCapability.serialize_element, element=Face)
    async def entity_face(self, element: Face) -> MessageFragment:
        return MessageFragmentEntity(
            str(element.name), MessageEntityType.CUSTOM_EMOJI, data={"custom_emoji_id": element.id}
        )
