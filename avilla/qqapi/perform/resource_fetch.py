from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import ClientSession

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.qqapi.resource import (
    QQAPIAudioResource,
    QQAPIFileResource,
    QQAPIImageResource,
    QQAPIResource,
    QQAPIVideoResource,
)

if TYPE_CHECKING:
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIResourceFetchPerform((m := ProtocolCollector["QQAPIProtocol"]())._):
    m.namespace = "avilla.protocol/qqapi::resource_fetch"

    @m.entity(CoreCapability.fetch, resource=QQAPIResource)
    @m.entity(CoreCapability.fetch, resource=QQAPIAudioResource)
    @m.entity(CoreCapability.fetch, resource=QQAPIFileResource)
    @m.entity(CoreCapability.fetch, resource=QQAPIImageResource)
    @m.entity(CoreCapability.fetch, resource=QQAPIVideoResource)
    async def fetch_resource(self, resource: QQAPIResource) -> bytes:
        async with ClientSession() as session:
            async with session.get(resource.url) as resp:
                return await resp.read()
