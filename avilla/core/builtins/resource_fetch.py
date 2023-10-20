from __future__ import annotations

from avilla.core.resource import LocalFileResource, RawResource
from avilla.core.ryanvk.collector.application import ApplicationCollector


class CoreResourceFetchPerform((m := ApplicationCollector())._):
    @m.fetch(LocalFileResource)
    async def fetch_localfile(self, res: LocalFileResource):
        return res.file.read_bytes()

    @m.fetch(RawResource)
    async def fetch_raw(self, res: RawResource):
        return res.data
