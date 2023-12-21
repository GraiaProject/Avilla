from __future__ import annotations

from typing import TYPE_CHECKING

from telegram import File

from avilla.core import RawResource
from avilla.core.elements import Audio, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.standard.telegram.elements import (
    Animation,
    Contact,
    Dice,
    DiceEmoji,
    Document,
    Location,
    Picture,
    Sticker,
    Venue,
    Video,
)
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import (
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
)
from avilla.telegram.resource import TelegramResource
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.telegram.account import TelegramAccount


class TelegramMessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = "avilla.protocol/telegram::message"
    m.identify = "deserialize"

    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[TelegramAccount] = OptionalAccess()
    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(TelegramCapability.deserialize_element, element="text")
    async def text(self, element: MessageFragmentText) -> Text:
        return Text(element.text)

    @m.entity(TelegramCapability.deserialize_element, element="photo")
    async def photo(self, element: MessageFragmentPhoto) -> Picture:
        if element.update:
            file: File = await element.file.get_file()
            resource = TelegramResource(
                Selector().land("telegram").picture(file).file_id(file.file_id).file_unique_id(file.file_unique_id),
                file,
                element.update.message.photo[-1],
                element.update.message.photo,
            )
            return Picture(resource, has_spoiler=element.has_spoiler)
        return Picture(RawResource(element.file), has_spoiler=element.has_spoiler)

    @m.entity(TelegramCapability.deserialize_element, element="animation")
    async def animation(self, element: MessageFragmentAnimation) -> Animation:
        if update := element.update:
            animation = update.message.animation
            file: File = await animation.get_file()
            resource = TelegramResource(
                Selector().land("telegram").animation(file).file_id(file.file_id).file_unique_id(file.file_unique_id),
                file,
                element.update.message.animation,
                (element.update.message.animation.thumbnail,),
            )
            return Animation(
                resource,
                width=animation.width,
                height=animation.height,
                duration=animation.duration,
                has_spoiler=element.has_spoiler,
            )
        return Animation(RawResource(element.file), has_spoiler=element.has_spoiler)

    @m.entity(TelegramCapability.deserialize_element, element="audio")
    async def audio(self, element: MessageFragmentAudio) -> Audio:
        if element.update:
            file: File = await element.update.message.audio.get_file()
            resource = TelegramResource(
                Selector().land("telegram").audio(file).file_id(file.file_id).file_unique_id(file.file_unique_id),
                file,
                element.update.message.audio,
                (element.update.message.audio.thumbnail,),
            )
            return Audio(resource, duration=element.update.message.audio.duration)
        return Audio(RawResource(element.file))

    @m.entity(TelegramCapability.deserialize_element, element="video")
    async def video(self, element: MessageFragmentVideo) -> Video:
        if element.update:
            file: File = await element.update.message.video.get_file()
            resource = TelegramResource(
                Selector().land("telegram").video(file).file_id(file.file_id).file_unique_id(file.file_unique_id),
                file,
                element.update.message.video,
                (element.update.message.video.thumbnail,),
            )
            return Video(resource, has_spoiler=element.has_spoiler)
        return Video(RawResource(element.file), has_spoiler=element.has_spoiler)

    @m.entity(TelegramCapability.deserialize_element, element="contact")
    async def contact(self, element: MessageFragmentContact) -> Contact:
        return Contact(element.phone_number, element.first_name, element.last_name, element.user_id, element.vcard)

    @m.entity(TelegramCapability.deserialize_element, element="dice")
    async def dice(self, element: MessageFragmentDice) -> Dice:
        return Dice(DiceEmoji(element.emoji), element.value)

    @m.entity(TelegramCapability.deserialize_element, element="document")
    async def document(self, element: MessageFragmentDocument) -> Document:
        if element.update:
            file: File = await element.update.message.audio.get_file()
            resource = TelegramResource(
                Selector().land("telegram").document(file).file_id(file.file_id).file_unique_id(file.file_unique_id),
                file,
                element.update.message.document,
                (element.update.message.document.thumbnail,),
            )
            return Document(resource)
        return Document(RawResource(element.file))

    @m.entity(TelegramCapability.deserialize_element, element="location")
    async def location(self, element: MessageFragmentLocation) -> Location:
        return Location(element.longitude, element.latitude)

    @m.entity(TelegramCapability.deserialize_element, element="sticker")
    async def sticker(self, element: MessageFragmentSticker) -> Sticker:
        if update := element.update:
            sticker = update.message.sticker
            file: File = await sticker.get_file()
            resource = TelegramResource(
                Selector().land("telegram").sticker(file).file_id(file.file_id).file_unique_id(file.file_unique_id),
                file,
                element.update.message.sticker,
                (element.update.message.sticker.thumbnail,),
            )
            return Sticker(
                resource,
                width=sticker.width,
                height=sticker.height,
                is_animated=sticker.is_animated,
                is_video=sticker.is_video,
            )
        return Sticker(RawResource(element.file))

    @m.entity(TelegramCapability.deserialize_element, element="venue")
    async def venue(self, element: MessageFragmentVenue) -> Venue:
        return Venue(element.latitude, element.longitude, element.title, element.address)

    # FIXME