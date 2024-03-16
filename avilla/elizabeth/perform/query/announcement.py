from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Callable, cast

from graia.amnesia.builtins.memcache import MemcacheService

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethAnnouncementQueryPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::query"
    m.identify = "announcement"

    @CoreCapability.query.collect(m, "announcement", "land.group")
    async def query_group_announcement(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.connection.call(
            "fetch", "anno_list", {"id": int(previous["group"]), "offset": 0, "size": 1}
        )
        result = cast(list, result)
        for i in result:
            announce_id = str(i["fid"])
            await cache.set(
                f"elizabeth/account({self.account.route['account']}).group({previous['group']}).announcement({announce_id})",
                i,
                timedelta(minutes=5),
            )
            if callable(predicate) and predicate("announcement", announce_id) or announce_id == predicate:
                yield Selector().land(self.account.route["land"]).group(previous["group"]).announcement(announce_id)
