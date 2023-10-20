from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, cast

from avilla.core.exceptions import UnknownTarget
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.privilege import MuteCapability, MuteInfo
from avilla.standard.core.profile import Nick, Summary
from graia.amnesia.builtins.memcache import Memcache, MemcacheService

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedMemberActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.namespace = "avilla.protocol/red::action"
    m.identify = "member"

    @m.pull("land.group.member", Summary)
    async def get_summary(self, target: Selector, route: ...) -> Summary:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(
            f"red/account({self.account.route['account']}).group({target.pattern['group']}).member({target.pattern['member']})"
        ):
            return Summary(raw["nick"], "a member of this group")
        result = await self.account.websocket_client.call_http(
            "get", "api/group/getMemberList", {"group": target.pattern["group"]}
        )
        result = cast(list, result)
        for i in result:
            member_id = str(i["uin"])
            if member_id == target["member"]:
                return Summary(i["nick"], "name of member")
        raise UnknownTarget("Member not found")

    @m.pull("land.group.member", Nick)
    async def get_nick(self, target: Selector, route: ...) -> Nick:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(
            f"red/account({self.account.route['account']}).group({target.pattern['group']}).member({target.pattern['member']})"
        ):
            return Nick(raw["nick"], raw["remark"] or raw["nick"], raw["cardName"])
        result = await self.account.websocket_client.call_http(
            "get", "api/group/getMemberList", {"group": target.pattern["group"]}
        )
        result = cast(list, result)
        for i in result:
            member_id = str(i["uin"])
            if member_id == target["member"]:
                return Nick(i["nick"], i["card"], i["cardName"])
        raise UnknownTarget("Member not found")

    @m.pull("land.group.member", MuteInfo)
    async def get_mute_info(self, target: Selector, route: ...) -> MuteInfo:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if raw := await cache.get(
            f"red/account({self.account.route['account']}).group({target.pattern['group']}).member({target.pattern['member']})"
        ):
            return MuteInfo(
                raw["shutUpTime"] > 0,
                timedelta(seconds=raw["shutUpTime"]),
            )
        result = await self.account.websocket_client.call_http(
            "get", "api/group/getMemberList", {"group": target.pattern["group"]}
        )
        result = cast(list, result)
        for i in result:
            member_id = str(i["uin"])
            if member_id == target["member"]:
                return MuteInfo(
                    i["shutUpTime"] > 0,
                    timedelta(seconds=i["shutUpTime"]),
                )
        raise UnknownTarget("Member not found")

    @m.entity(MuteCapability.mute, target="land.group.member")
    async def group_member_mute(self, target: Selector, duration: timedelta):
        time = max(60.0, min(duration.total_seconds(), 2592000))
        await self.account.websocket_client.call_http(
            "post",
            "api/group/muteMember",
            {"group": int(target["group"]), "memList": [{"uin": int(target["member"]), "timeStamp": time}]},
        )

    @m.entity(MuteCapability.unmute, target="land.group.member")
    async def group_member_unmute(self, target: Selector):
        await self.account.websocket_client.call_http(
            "post",
            "api/group/muteMember",
            {"group": int(target["group"]), "memList": [{"uin": int(target["member"]), "timeStamp": 0}]},
        )
