from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core.elements import Picture, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerialize
from avilla.telegram.elements import (
    MessageFragment,
    MessageFragmentPhoto,
    MessageFragmentText,
)
from avilla.telegram.resource import TelegramPhotoResource

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa

TelegramMessageSerialize = MessageSerialize[MessageFragment]


class TelegramMessageSerializePerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @TelegramMessageSerialize.collect(m, Text)
    async def text(self, element: Text) -> MessageFragment:
        return MessageFragmentText(element.text)

    @TelegramMessageSerialize.collect(m, Picture)
    async def picture(self, element: Picture) -> MessageFragment:
        return MessageFragmentPhoto(
            resource.file
            if isinstance(resource := element.resource, TelegramPhotoResource)
            else cast(bytes, await self.account.staff.fetch_resource(resource))
        )

    # TODO
