from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import ClientSession

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.protocol import ProtocolCollector
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
    m.namespace = "avilla.protocol/onebot11::resource_fetch"

    @m.entity(CoreCapability.fetch, resource=OneBot11Resource)
    @m.entity(CoreCapability.fetch, resource=OneBot11RecordResource)
    @m.entity(CoreCapability.fetch, resource=OneBot11FileResource)
    @m.entity(CoreCapability.fetch, resource=OneBot11ImageResource)
    @m.entity(CoreCapability.fetch, resource=OneBot11VideoResource)
    async def fetch_resource(self, resource: OneBot11Resource) -> bytes:
        async with ClientSession() as session:
            async with session.get(resource.url) as resp:
                return await resp.read()
