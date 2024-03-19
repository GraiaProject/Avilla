from __future__ import annotations

from aiohttp import ClientSession

from avilla.core.builtins.capability import CoreCapability
from avilla.onebot.v11.resource import (
    OneBot11FileResource,
    OneBot11ImageResource,
    OneBot11RecordResource,
    OneBot11Resource,
    OneBot11VideoResource,
)
from flywheel import global_collect

@global_collect
@CoreCapability.fetch.impl(resource=OneBot11RecordResource)  # type: ignore
@CoreCapability.fetch.impl(resource=OneBot11FileResource)  # type: ignore
@CoreCapability.fetch.impl(resource=OneBot11ImageResource)  # type: ignore
@CoreCapability.fetch.impl(resource=OneBot11VideoResource)
@CoreCapability.fetch.impl(resource=OneBot11Resource)
async def fetch_resource(resource: OneBot11Resource) -> bytes:
    async with ClientSession() as session:
        async with session.get(resource.url) as resp:
            return await resp.read()
