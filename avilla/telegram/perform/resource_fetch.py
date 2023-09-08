from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.core.ryanvk.descriptor.fetch import Fetch
from avilla.telegram.resource import (
    TelegramFileResource,
    TelegramPhotoResource,
    TelegramRecordResource,
    TelegramResource,
    TelegramVideoResource,
)

if TYPE_CHECKING:
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramResourceFetchPerform((m := ProtocolCollector["TelegramProtocol"]())._):
    m.post_applying = True

    @Fetch.collect(m, TelegramResource)
    @Fetch.collect(m, TelegramRecordResource)
    @Fetch.collect(m, TelegramFileResource)
    @Fetch.collect(m, TelegramPhotoResource)
    @Fetch.collect(m, TelegramVideoResource)
    async def fetch_resource(self, resource: TelegramResource) -> bytes:
        b_io = BytesIO()
        await resource.file.download_to_memory(b_io)
        return b_io.getvalue()
