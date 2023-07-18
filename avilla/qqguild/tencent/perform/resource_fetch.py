from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import ClientSession

from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.core.ryanvk.descriptor.fetch import Fetch
from avilla.qqguild.tencent.resource import QQGuildImageResource, QQGuildResource

if TYPE_CHECKING:
    from ..protocol import QQGuildProtocol  # noqa


class QQGuildResourceFetchPerform((m := ProtocolCollector["QQGuildProtocol"]())._):
    m.post_applying = True

    @Fetch.collect(m, QQGuildResource)
    @Fetch.collect(m, QQGuildImageResource)
    async def fetch_resource(self, resource: QQGuildResource) -> bytes:
        async with ClientSession() as session:
            async with session.get(resource.url) as resp:
                return await resp.read()
