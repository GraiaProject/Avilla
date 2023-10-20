from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import ClientSession
from base64 import b64decode

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.satori.resource import (
    SatoriImageResource,
    SatoriVideoResource,
    SatoriAudioResource,
    SatoriFileResource,
    SatoriResource
)

if TYPE_CHECKING:
    from avilla.satori.protocol import SatoriProtocol  # noqa


class SatoriResourceFetchPerform((m := ProtocolCollector["SatoriProtocol"]())._):
    m.namespace = "avilla.protocol/satori::resource_fetch"

    @m.entity(CoreCapability.fetch, resource=SatoriResource)
    @m.entity(CoreCapability.fetch, resource=SatoriImageResource)
    @m.entity(CoreCapability.fetch, resource=SatoriVideoResource)
    @m.entity(CoreCapability.fetch, resource=SatoriAudioResource)
    @m.entity(CoreCapability.fetch, resource=SatoriFileResource)  # type: ignore
    async def fetch_resource(self, resource: SatoriResource) -> bytes:
        if resource.src.startswith("file://"):
            with open(resource.src[7:], "rb") as f:
                return f.read()
        if resource.src.startswith("data:"):
            return b64decode(resource.src[5:].split(";", 1)[1][7:])
        async with ClientSession() as session:
            async with session.get(resource.src) as resp:
                return await resp.read()
