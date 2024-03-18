from __future__ import annotations

from avilla.core.flywheel.scoped import scoped_collect
from avilla.core.resource import LocalFileResource, RawResource, UrlResource

try:
    from aiohttp import ClientSession
except ImportError:
    ClientSession = None

from .capability import CoreCapability


class CoreResourceFetchPerform(m := scoped_collect.globals().target):
    @m.impl(CoreCapability.fetch, resource=LocalFileResource)
    async def fetch_localfile(self, resource: LocalFileResource):
        return resource.file.read_bytes()

    @m.impl(CoreCapability.fetch, resource=RawResource)
    async def fetch_raw(self, resource: RawResource):
        return resource.data

    if ClientSession is not None:

        @m.impl(CoreCapability.fetch, resource=UrlResource)
        async def fetch_url(self, resource: UrlResource):
            async with ClientSession() as session:  # type: ignore
                async with session.get(resource.url) as resp:
                    return await resp.read()
