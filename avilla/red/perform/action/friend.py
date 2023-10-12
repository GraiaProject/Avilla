from __future__ import annotations

from typing import TYPE_CHECKING, cast

from avilla.core.exceptions import UnknownTarget
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Nick, Summary
from graia.amnesia.builtins.memcache import Memcache, MemcacheService

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedFriendActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.namespace = "avilla.protocol/red::action"
    m.identify = "friend"

    @m.pull("land.friend", Summary)
    async def get_summary(self, target: Selector, route: ...) -> Summary:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"red/account({self.account.route['account']}).friend({target.pattern['friend']})"):
            return Summary(raw["nick"], "a friend contact assigned to this account")
        result = await self.account.websocket_client.call_http("get", "api/bot/friends", {})
        result = cast(list, result)
        for i in result:
            friend_id = str(i["uin"])
            if friend_id == target["friend"]:
                return Summary(i["nick"], "name of friend")
        raise UnknownTarget("Friend not found")

    @m.pull("land.friend", Nick)
    async def get_nick(self, target: Selector, route: ...) -> Nick:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"red/account({self.account.route['account']}).friend({target.pattern['friend']})"):
            return Nick(raw["nick"], raw["remark"] or raw["nick"], raw["longNick"])
        result = await self.account.websocket_client.call_http("get", "api/bot/friends", {})
        result = cast(list, result)
        for i in result:
            friend_id = str(i["uin"])
            if friend_id == target["friend"]:
                return Nick(i["nick"], i["remark"], i["longNick"])
        raise UnknownTarget("Friend not found")
