from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Callable, cast

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from graia.amnesia.builtins.memcache import Memcache, MemcacheService

if TYPE_CHECKING:
    from ..account import RedAccount  # noqa
    from ..protocol import RedProtocol  # noqa


class RedQueryPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.namespace = "avilla.protocol/red::query"

    @m.entity(CoreCapability.query, target="land.group")
    async def query_group(self, predicate: Callable[[str, str], bool] | str, previous: None):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.websocket_client.call_http("get", "api/bot/groups", {})
        result = cast(list, result)
        for i in result:
            group_id = str(i["groupCode"])
            await cache.set(f"red/account({self.account.route['account']}).group({group_id})", i, timedelta(minutes=5))
            if callable(predicate) and predicate("group", group_id) or group_id == predicate:
                yield Selector().land(self.account.route["land"]).group(group_id)

    @m.entity(CoreCapability.query, target="land.friend")
    async def query_friend(self, predicate: Callable[[str, str], bool] | str, previous: None):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.websocket_client.call_http("get", "api/bot/friends", {})
        result = cast(list, result)
        for i in result:
            friend_id = str(i["uin"])
            await cache.set(
                f"red/account({self.account.route['account']}).friend({friend_id})", i, timedelta(minutes=5)
            )
            if callable(predicate) and predicate("friend", friend_id) or friend_id == predicate:
                yield Selector().land(self.account.route["land"]).friend(friend_id)

    @m.entity(CoreCapability.query, target="member", previous="land.group")  # type: ignore
    async def query_group_members(self, predicate: Callable[[str, str], bool] | str, previous: Selector):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        result = await self.account.websocket_client.call_http(
            "post", "api/group/getMemberList", {"group": int(previous["group"])}
        )
        result = cast(list, result)
        for i in result:
            member_id = str(i["uin"])
            await cache.set(
                f"red/account({self.account.route['account']}).group({previous['group']}).member({member_id})",
                i,
                timedelta(minutes=5),
            )
            if callable(predicate) and predicate("member", member_id) or member_id == predicate:
                yield previous.member(member_id)
