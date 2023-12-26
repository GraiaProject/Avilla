from __future__ import annotations

from avilla.core.resource import LocalFileResource, RawResource, UrlResource
from avilla.core.ryanvk.collector.application import ApplicationCollector

try:
    from aiohttp import ClientSession

    aio = True
except ImportError:
    ClientSession = None
    aio = False

from .capability import CoreCapability


class CoreResourceFetchPerform((m := ApplicationCollector())._):
    @m.entity(CoreCapability.fetch, resource=LocalFileResource)
    async def fetch_localfile(self, resource: LocalFileResource):
        return resource.file.read_bytes()

    @m.entity(CoreCapability.fetch, resource=RawResource)
    async def fetch_raw(self, resource: RawResource):
        return resource.data

    if aio:

        @m.entity(CoreCapability.fetch, resource=UrlResource)
        async def fetch_url(self, resource: UrlResource):
            async with ClientSession() as session:
                async with session.get(resource.url) as resp:
                    return await resp.read()

    else:

        @m.entity(CoreCapability.fetch, resource=UrlResource)
        async def fetch_url(self, resource: UrlResource):
            raise NotImplementedError("aiohttp is not installed")
