from __future__ import annotations

from ..resource import LocalFileResource, RawResource
from ..ryanvk.collector.application import ApplicationCollector


class CoreResourceFetchPerform((m := ApplicationCollector())._):
    
    async def fetch_localfile(self, res: LocalFileResource):
        return res.file.read_bytes()

    async def fetch_raw(self, res: RawResource):
        return res.data
