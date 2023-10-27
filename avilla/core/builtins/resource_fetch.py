from __future__ import annotations

from avilla.core.resource import LocalFileResource, RawResource
from avilla.core.ryanvk.collector.application import ApplicationCollector

from .capability import CoreCapability


class CoreResourceFetchPerform((m := ApplicationCollector())._):
    @m.entity(CoreCapability.fetch, resource=LocalFileResource)
    async def fetch_localfile(self, resource: LocalFileResource):
        return resource.file.read_bytes()

    @m.entity(CoreCapability.fetch, resource=RawResource)
    async def fetch_raw(self, resource: RawResource):
        return resource.data
