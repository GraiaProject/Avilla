from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import ClientSession

from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.core.ryanvk.descriptor.fetch import Fetch
from avilla.onebot.v11.resource import (
    OneBot11FileResource,
    OneBot11ImageResource,
    OneBot11RecordResource,
    OneBot11Resource,
    OneBot11VideoResource,
)

if TYPE_CHECKING:
    from avilla.onebot.v11.protocol import OneBot11Protocol  # noqa


class OneBot11ResourceFetchPerform((m := ProtocolCollector["OneBot11Protocol"]())._):
    m.post_applying = True

    @Fetch.collect(m, OneBot11Resource)
    @Fetch.collect(m, OneBot11RecordResource)
    @Fetch.collect(m, OneBot11FileResource)
    @Fetch.collect(m, OneBot11ImageResource)
    @Fetch.collect(m, OneBot11VideoResource)
    async def fetch_resource(self, resource: OneBot11Resource) -> bytes:
        async with ClientSession() as session:
            async with session.get(resource.url) as resp:
                return await resp.read()
