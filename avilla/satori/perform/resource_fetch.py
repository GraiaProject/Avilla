from __future__ import annotations

from base64 import b64decode

from aiohttp import ClientSession
from flywheel import global_collect

from avilla.core.builtins.capability import CoreCapability
from avilla.satori.resource import (
    SatoriAudioResource,
    SatoriFileResource,
    SatoriImageResource,
    SatoriResource,
    SatoriVideoResource,
)


@global_collect
@CoreCapability.fetch.impl(resource=SatoriImageResource)  # type: ignore
@CoreCapability.fetch.impl(resource=SatoriVideoResource)  # type: ignore
@CoreCapability.fetch.impl(resource=SatoriAudioResource)  # type: ignore
@CoreCapability.fetch.impl(resource=SatoriFileResource)
@CoreCapability.fetch.impl(resource=SatoriResource)
async def fetch_resource(resource: SatoriResource) -> bytes:
    if resource.src.startswith("file://"):
        with open(resource.src[7:], "rb") as f:
            return f.read()
    if resource.src.startswith("data:"):
        return b64decode(resource.src[5:].split(";", 1)[1][7:])
    async with ClientSession() as session:
        async with session.get(resource.src) as resp:
            return await resp.read()
