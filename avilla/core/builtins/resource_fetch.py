from __future__ import annotations

from avilla.core.resource import LocalFileResource, RawResource
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.fetch import Fetch


class CoreResourceFetchPerform((m := ApplicationCollector())._):
    @m.entity(Fetch, LocalFileResource)
    @Fetch.collect(m, LocalFileResource)
    async def fetch_localfile(self, res: LocalFileResource):
        return res.file.read_bytes()

    @m.entity(Fetch, RawResource)
    async def fetch_raw(self, res: RawResource):
        return res.data
