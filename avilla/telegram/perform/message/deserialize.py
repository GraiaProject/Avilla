from __future__ import annotations

from typing import TYPE_CHECKING

from telegram import File

from avilla.core.elements import Picture, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.standard.telegram.elements import Contact, Dice, DiceEmoji, Location, Venue
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import (
    MessageFragmentContact,
    MessageFragmentDice,
    MessageFragmentLocation,
    MessageFragmentPhoto,
    MessageFragmentText,
    MessageFragmentVenue,
)
from avilla.telegram.resource import TelegramPhotoResource
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
        file: File = await element.file.get_file()
        resource = TelegramPhotoResource(Selector().land("telegram").picture(file), file, element.update.message.photo)
        return Picture(resource)

    @m.entity(TelegramCapability.deserialize_element, element="contact")
    async def contact(self, element: MessageFragmentContact) -> Contact:
        return Contact(element.phone_number, element.first_name, element.last_name, element.user_id, element.vcard)

    @m.entity(TelegramCapability.deserialize_element, element="dice")
    async def dice(self, element: MessageFragmentDice) -> Dice:
        return Dice(DiceEmoji(element.emoji), element.value)

    @m.entity(TelegramCapability.deserialize_element, element="location")
    async def location(self, element: MessageFragmentLocation) -> Location:
        return Location(element.longitude, element.latitude)

    @m.entity(TelegramCapability.deserialize_element, element="venue")
    async def venue(self, element: MessageFragmentVenue) -> Venue:
        return Venue(element.latitude, element.longitude, element.title, element.address)

    # TODO
