from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Callable, cast

from graia.amnesia.builtins.memcache import Memcache, MemcacheService

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethGroupQueryPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::query"
    m.identify = "group"

    @CoreCapability.query.collect(m, "land.group")
    async def query_group(self, predicate: Callable[[str, str], bool] | str, previous: None):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.connection.call("fetch", "groupList", {})
        result = cast(list, result)
        for i in result:
            group_id = str(i["id"])
            await cache.set(
                f"elizabeth/account({self.account.route['account']}).group({group_id})", i, timedelta(minutes=5)
            )
            if callable(predicate) and predicate("group", group_id) or group_id == predicate:
                yield Selector().land(self.account.route["land"]).group(group_id)

    @CoreCapability.query.collect(m, "member", "land.group")
    async def query_group_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.connection.call(
            "fetch", "latestMemberList", {"target": int(previous["group"]), "memberIds": []}
        )
        if isinstance(predicate, str) and predicate == str(self.account.route["account"]):
            yield previous.member(predicate)  # bot self not in memberList
            return
        result = cast(list, result)
        for i in result:
            member_id = str(i["id"])
            await cache.set(
                f"elizabeth/account({self.account.route['account']}).group({i['group']['id']}).member({member_id})",
                i,
                timedelta(minutes=5),
            )
            if callable(predicate) and predicate("member", member_id) or member_id == predicate:
                yield previous.member(member_id)
