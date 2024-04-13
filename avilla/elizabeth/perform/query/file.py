from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Callable, cast

from graia.amnesia.builtins.memcache import MemcacheService

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.elizabeth.utils import filedata_parse

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethFileQueryPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::query"
    m.identify = "file"

    @CoreCapability.query.collect(m, "file", "land.group")
    async def query_group_file(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.connection.call(
            "fetch", "file_list", {"id": "", "target": int(previous["group"]), "offset": 0, "size": 1, "withDownloadInfo": "True"}
        )
        result = cast(list, result)
        for i in result:
            file_id = i["id"]
            await cache.set(
                f"elizabeth/account({self.account.route['account']}).group({previous['group']}).file({file_id})",
                filedata_parse(i),
                timedelta(minutes=5),
            )
            if callable(predicate) and predicate("file", file_id) or file_id == predicate:
                yield Selector().land(self.account.route["land"]).group(previous["group"]).file(file_id)
