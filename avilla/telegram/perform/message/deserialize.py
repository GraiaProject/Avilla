from __future__ import annotations

from typing import TYPE_CHECKING

from telegram import File

from avilla.core.elements import Picture, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import MessageFragmentPhoto, MessageFragmentText
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
    async def text(self, raw_update: MessageFragmentText) -> Text:
        return Text(raw_update.text)

    @m.entity(TelegramCapability.deserialize_element, element="photo")
    async def photo(self, raw_update: MessageFragmentPhoto) -> Picture:
        file: File = await raw_update.file.get_file()
        resource = TelegramPhotoResource(
            Selector().land("telegram").picture(file), file, raw_update.update.message.photo
        )
        return Picture(resource)

    # TODO
