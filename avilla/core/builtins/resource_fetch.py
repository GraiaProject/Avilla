from __future__ import annotations

from ..resource import LocalFileResource, RawResource
from ..ryanvk.collector.application import ApplicationCollector
from ..ryanvk.descriptor.fetch import Fetch


class CoreResourceFetchPerform((m := ApplicationCollector())._):
    @Fetch.collect(m, LocalFileResource)
    async def fetch_localfile(self, res: LocalFileResource):
        return res.file.read_bytes()

    @Fetch.collect(m, RawResource)
    async def fetch_raw(self, res: RawResource):
        return res.data
