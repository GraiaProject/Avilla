from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService

from avilla.core.exceptions import permission_error_message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.elizabeth.const import PRIVILEGE_LEVEL, PRIVILEGE_TRANS
from avilla.standard.core.privilege import (
    MuteCapability,
    MuteInfo,
    Privilege,
    PrivilegeCapability,
)
from avilla.standard.core.profile import Avatar, Nick, NickCapability, Summary
from avilla.standard.core.relation import SceneCapability

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethGroupMemberActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.namespace = "avilla.protocol/elizabeth::action"
    m.identify = "member"

    @m.pull("land.group.member", Avatar)
    async def get_group_member_avatar(self, target: Selector, route: ...) -> Avatar:
        return Avatar(f"https://q2.qlogo.cn/headimg_dl?dst_uin={target.pattern['member']}&spec=640")

    @m.pull("land.group.member", Nick)
    async def get_group_member_nick(self, target: Selector, route: ...) -> Nick:
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if not (
            result := await cache.get(
                f"elizabeth/account({self.account.route['account']}).group({target.pattern['group']}).member({target.pattern['member']})"
            )
        ):
            result = await self.account.connection.call(
                "fetch",
                "memberInfo",
                {
                    "target": int(target.pattern["group"]),
                    "memberId": int(target.pattern["member"]),
                },
            )
        result1 = await self.account.connection.call(
            "fetch",
            "memberProfile",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )
        return Nick(result1["nickname"], result["memberName"], result.get("specialTitle"))

    @m.entity(NickCapability.set_nickname, target="land.group.member")
    async def set_group_member_nick(self, target: Selector, nickname: str):
        privilege_info = await self.get_group_member_privilege(target, Privilege)
        if not privilege_info.available:
            self_permission = await self.get_group_member_privilege_summary(
                target.into(f"~.member({self.account.route['account']})"), Summary
            )
            raise PermissionError(
                permission_error_message(
                    f"set_name@{target.path}", self_permission.name, ["group_owner", "group_admin"]
                )
            )
        await self.account.connection.call(
            "update",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
                "info": {
                    "name": nickname,
                },
            },
        )

    @m.entity(NickCapability.set_badge, target="land.group.member")
    async def set_group_member_badge(self, target: Selector, badge: str):
        privilege_info = await self.get_group_member_privilege_privilege(target, Privilege)
        if not privilege_info.available:
            self_permission = await self.get_group_member_privilege_summary(
                target.into(f"~.member({self.account.route['account']})"), Summary
            )
            raise PermissionError(
                permission_error_message(f"mute@{target.path}", self_permission.name, ["group_owner"])
            )
        await self.account.connection.call(
            "update",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
                "info": {
                    "specialTitle": badge,
                },
            },
        )

    @m.pull("land.group.member", MuteInfo)
    async def get_group_member_mute_info(self, target: Selector, route: ...) -> MuteInfo:
        cache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if not (
            result := await cache.get(
                f"elizabeth/account({self.account.route['account']}).group({target.pattern['group']}).member({target.pattern['member']})"
            )
        ):
            result = await self.account.connection.call(
                "fetch",
                "memberInfo",
                {
                    "target": int(target.pattern["group"]),
                    "memberId": int(target.pattern["member"]),
                },
            )
        return MuteInfo(
            result.get("mutetimeRemaining") is not None,
            timedelta(seconds=result.get("mutetimeRemaining", 0)),
            None,
        )

    @m.entity(MuteCapability.mute, target="land.group.member")
    async def group_member_mute(self, target: Selector, duration: timedelta):
        privilege_info = await self.get_group_member_privilege(target, Privilege)
        if not privilege_info.effective:
            self_permission = await self.get_group_member_privilege_summary(
                target.into(f"~.member({self.account.route['account']})"), Summary
            )
            raise PermissionError(
                permission_error_message(f"mute@{target.path}", self_permission.name, ["group_owner", "group_admin"])
            )
        time = max(0, min(int(duration.total_seconds()), 2592000))
        if not time:
            return
        await self.account.connection.call(
            "update",
            "mute",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
                "time": time,
            },
        )

    @m.entity(MuteCapability.unmute, target="land.group.member")
    async def group_member_unmute(self, target: Selector):
        privilege_info = await self.get_group_member_privilege(target, Privilege)
        if not privilege_info.effective:
            self_permission = await self.get_group_member_privilege_summary(
                target.into(f"~.member({self.account.route['account']})"), Summary
            )
            raise PermissionError(
                permission_error_message(f"unmute@{target.path}", self_permission.name, ["group_owner", "group_admin"])
            )
        await self.account.connection.call(
            "update",
            "unmute",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )

    @m.pull("land.group.member", Privilege)
    async def get_group_member_privilege(self, target: Selector, route: ...) -> Privilege:
        if target.pattern["member"] == self.account.route["account"]:
            return Privilege(True, True)
        self_info = await self.account.connection.call(
            "fetch",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(self.account.route["account"]),
            },
        )
        target_info = await self.account.connection.call(
            "fetch",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )
        return Privilege(
            PRIVILEGE_LEVEL[target_info["permission"]] > 0,
            PRIVILEGE_LEVEL[self_info["permission"]] > PRIVILEGE_LEVEL[target_info["permission"]],
        )

    @m.pull("land.group.member", Privilege >> Summary)
    async def get_group_member_privilege_summary(self, target: Selector, route: ...) -> Summary:
        target_info = await self.account.connection.call(
            "fetch",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )
        return Summary(
            PRIVILEGE_TRANS[target_info["permission"]], "the permission info of current account in the group"
        ).infers(Privilege >> Summary)

    @m.pull("land.group.member", Privilege >> Privilege)
    async def get_group_member_privilege_privilege(self, target: Selector, route: ...) -> Privilege:
        self_info = await self.account.connection.call(
            "fetch",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(self.account.route["account"]),
            },
        )
        result = await self.account.connection.call(
            "fetch",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )
        return Privilege(
            PRIVILEGE_LEVEL[result["permission"]] == 2,
            PRIVILEGE_LEVEL[self_info["permission"]] > PRIVILEGE_LEVEL[result["permission"]],
        ).infers(Privilege >> Privilege)

    @m.pull("land.group.member", Privilege >> Privilege >> Summary)
    async def get_group_member_privilege_privilege_summary(self, target: Selector, route: ...) -> Summary:
        target_info = await self.account.connection.call(
            "fetch",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )
        return Summary(
            PRIVILEGE_TRANS[target_info["permission"]],
            "the permission of controling administration of the group,"
            "to be noticed that is only group owner could do this.",
        ).infers(Privilege >> Privilege >> Summary)

    @m.entity(PrivilegeCapability.upgrade, target="land.group.member")
    async def group_member_upgrade(self, target: Selector, dest: str | None = None):
        if not (await self.get_group_member_privilege_privilege(target, Privilege)).available:
            self_privilege_info = await self.get_group_member_privilege_summary(
                target.into(f"~.member({self.account.route['account']})"), Summary
            )
            raise PermissionError(
                permission_error_message(f"upgrade_permission@{target.path}", self_privilege_info.name, ["group_owner"])
            )
        await self.account.connection.call(
            "update",
            "memberAdmin",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
                "assign": True,
            },
        )

    @m.entity(PrivilegeCapability.downgrade, target="land.group.member")
    async def group_member_downgrade(self, target: Selector, dest: str | None = None):
        if not (await self.get_group_member_privilege_privilege(target, Privilege)).available:
            self_privilege_info = await self.get_group_member_privilege_summary(
                target.into(f"~.member({self.account.route['account']})"), Summary
            )
            raise PermissionError(
                permission_error_message(
                    f"downgrade_permission@{target.path}", self_privilege_info.name, ["group_owner"]
                )
            )
        await self.account.connection.call(
            "update",
            "memberAdmin",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
                "assign": False,
            },
        )

    @m.entity(SceneCapability.remove_member, target="land.group.member")
    async def group_member_remove(self, target: Selector, reason: str | None = None, permanent: bool = False):
        if not (await self.get_group_member_privilege(target, Privilege)).effective:
            self_privilege_info = await self.get_group_member_privilege_summary(
                target.into(f"~.member({self.account.route['account']})"), Summary
            )
            raise PermissionError(
                permission_error_message(
                    f"remove_member@{target.path}", self_privilege_info.name, ["group_owner", "group_admin"]
                )
            )
        await self.account.connection.call(
            "update",
            "kick",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )
