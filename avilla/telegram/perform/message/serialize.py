from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core.elements import Picture, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import (
    MessageFragment,
    MessageFragmentPhoto,
    MessageFragmentText,
)
from avilla.telegram.resource import TelegramPhotoResource

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
        return MessageFragmentPhoto(
            resource.file
            if isinstance(resource := element.resource, TelegramPhotoResource)
            else cast(bytes, await self.account.staff.fetch_resource(resource))
        )

    # TODO
