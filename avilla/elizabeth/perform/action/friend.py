from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Avatar, Nick, Summary
from avilla.standard.core.relation.capability import RelationshipTerminate

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethFriendActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::action"
    m.identify = "friend"

    @m.pull("land.friend", Avatar)
    async def get_friend_avatar(self, target: Selector, route: ...) -> Avatar:
        return Avatar(f"https://q2.qlogo.cn/headimg_dl?dst_uin={target.pattern['friend']}&spec=640")

    @m.pull("land.friend", Nick)
    async def get_friend_nick(self, target: Selector, route: ...) -> Nick:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(
            f"elizabeth/account({self.account.route['account']}).friend({target.pattern['friend']})"
        ):
            return Nick(raw["nickname"], raw["remark"] or raw["nickname"], None)
        result = await self.account.connection.call(
            "fetch",
            "friendProfile",
            {
                "target": int(target.pattern["friend"]),
            },
        )
        return Nick(result["nickname"], result["nickname"], None)

    @m.pull("land.friend", Summary)
    async def get_friend_summary(self, target: Selector, route: ...) -> Summary:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(
            f"elizabeth/account({self.account.route['account']}).friend({target.pattern['friend']})"
        ):
            return Summary(raw["nickname"], "a friend contact assigned to this account")
        result = await self.account.connection.call(
            "fetch",
            "friendProfile",
            {
                "target": int(target.pattern["friend"]),
            },
        )
        return Summary(result["nickname"], "a friend contact assigned to this account")

    @RelationshipTerminate.terminate.collect(m, target="land.friend")
    async def friend_terminate(self, target: Selector):
        await self.account.connection.call(
            "update",
            "deleteFriend",
            {
                "target": int(target.pattern["friend"]),
            },
        )
