from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core import LocalFileResource, RawResource, UrlResource
from avilla.core.builtins.resource_fetch import CoreResourceFetchPerform
from avilla.core.elements import Audio, Picture, Text, Video
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.fragments import (
    MessageFragment,
    MessageFragmentAudio,
    MessageFragmentPhoto,
    MessageFragmentText,
    MessageFragmentVideo,
)
from avilla.telegram.resource import TelegramPhotoResource, TelegramThumbedResource

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
        if isinstance(resource := element.resource, TelegramPhotoResource):
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
        if isinstance(resource := element.resource, TelegramThumbedResource):
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
        if isinstance(resource := element.resource, TelegramThumbedResource):
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

    # TODO
