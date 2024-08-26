from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import Avatar, Nick, Summary
from avilla.standard.core.relation import SceneCapability

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class OneBot11BanActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::action"
    m.identify = "scene"

    @SceneCapability.leave.collect(m, target="land.group")
    async def leave_group(self, target: Selector):
        result = await self.account.connection.call(
            "set_group_leave", {"group_id": int(target["group"]), "is_dismiss": False}
        )
        if result is not None:
            raise RuntimeError(f"Failed to leave {target}: {result}")

    @SceneCapability.disband.collect(m, target="land.group")
    async def disband_group(self, target: Selector):
        result = await self.account.connection.call(
            "set_group_leave", {"group_id": int(target["group"]), "is_dismiss": True}
        )
        if result is not None:
            raise RuntimeError(f"Failed to disband {target}: {result}")

    @SceneCapability.remove_member.collect(m, target="land.group.member")
    async def kick_member(self, target: Selector, reason: str | None = None, permanent: bool = False):
        result = await self.account.connection.call(
            "set_group_kick",
            {
                "group_id": int(target["group"]),
                "user_id": int(target["member"]),
                "reject_add_request": permanent,
            },
        )
        if result is not None:
            raise RuntimeError(f"Failed to ban {target}: {result}")

    @m.pull("land.group.member", Nick)
    async def get_member_nick(self, target: Selector, route: ...) -> Nick:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(
            f"onebot11/account({self.account.route['account']}).group({target['group']}).member({target['member']})"
        ):
            return Nick(raw.get("card", "") or raw["nickname"], raw["nickname"], raw.get("title"))
        result = await self.account.connection.call(
            "get_group_member_info",
            {"group_id": int(target["group"]), "user_id": int(target["member"]), "no_cache": True},
        )
        if result is None:
            raise RuntimeError(f"Failed to get member {target}")
        return Nick(result.get("card", "") or result["nickname"], result["nickname"], result.get("title"))

    @m.pull("land.friend", Nick)
    async def get_friend_nick(self, target: Selector, route: ...) -> Nick:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"onebot11/account({self.account.route['account']}).friend({target['friend']})"):
            return Nick(raw["nickname"], raw.get("remark") or raw["nickname"], None)
        if not (results := await self.account.connection.call("get_friend_list")):
            raise RuntimeError(f"Failed to get friend {target}")
        if not (result := next(filter(lambda x: x["user_id"] == int(target["friend"]), results), None)):
            raise RuntimeError(f"Failed to get friend {target}")
        return Nick(result["nickname"], result.get("remark") or result["nickname"], None)

    @m.pull("land.stranger", Nick)
    async def get_stranger_nick(self, target: Selector, route: ...) -> Nick:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"onebot11/account({self.account.route['account']}).stranger({target['stranger']})"):
            return Nick(raw["nickname"], raw["nickname"], None)
        result = await self.account.connection.call(
            "get_stranger_info ", {"user_id": int(target["stranger"]), "no_cache": True}
        )
        if result is None:
            raise RuntimeError(f"Failed to get stranger {target}")
        return Nick(result["nickname"], result["nickname"], None)

    @m.pull("land.group", Summary)
    async def get_group_summary(self, target: Selector, route: ...) -> Summary:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"onebot11/account({self.account.route['account']}).group({target['group']})"):
            return Summary(raw["group_name"], None)
        result = await self.account.connection.call(
            "get_group_info", {"group_id": int(target["group"]), "no_cache": True}
        )
        if result is None:
            raise RuntimeError(f"Failed to get group {target}")
        return Summary(result["group_name"], None)

    @m.pull("land.friend", Summary)
    async def get_friend_summary(self, target: Selector, route: ...) -> Summary:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"onebot11/account({self.account.route['account']}).friend({target['friend']})"):
            return Summary(raw["nickname"], "a friend contact assigned to this account")
        if not (results := await self.account.connection.call("get_friend_list")):
            raise RuntimeError(f"Failed to get friend {target}")
        if not (result := next(filter(lambda x: x["user_id"] == int(target["friend"]), results), None)):
            raise RuntimeError(f"Failed to get friend {target}")
        return Summary(result["nickname"], "a friend contact assigned to this account")

    @m.pull("land.stranger", Summary)
    async def get_stranger_summary(self, target: Selector, route: ...) -> Summary:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(f"onebot11/account({self.account.route['account']}).stranger({target['stranger']})"):
            return Summary(raw["nickname"], None)
        result = await self.account.connection.call(
            "get_stranger_info ", {"user_id": int(target["stranger"]), "no_cache": True}
        )
        if result is None:
            raise RuntimeError(f"Failed to get stranger {target}")
        return Summary(result["nickname"], None)

    @m.pull("land.group.member", Avatar)
    @m.pull("land.friend", Avatar)
    @m.pull("land.stranger", Avatar)
    async def get_user_avatar(self, target: Selector, route: ...) -> Avatar:
        return Avatar(f"https://q2.qlogo.cn/headimg_dl?dst_uin={target.last_value}&spec=640")

    @m.pull("land.group", Avatar)
    async def get_group_avatar(self, target: Selector, route: ...) -> Avatar:
        return Avatar(f"https://p.qlogo.cn/gh/{target['group']}/{target['group']}/")
