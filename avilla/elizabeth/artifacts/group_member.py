from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from avilla.core.exceptions import permission_error_message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull
from avilla.elizabeth.const import privilege_level, privilege_trans
from avilla.spec.core.activity.skeleton import ActivityTrigger
from avilla.spec.core.privilege import MuteTrait, Privilege
from avilla.spec.core.privilege.metadata import MuteInfo
from avilla.spec.core.privilege.skeleton import PrivilegeTrait
from avilla.spec.core.profile import Nick, Summary
from avilla.spec.core.scene.skeleton import SceneTrait

if TYPE_CHECKING:
    from avilla.core.context import Context

with bounds("group.member"):

    @pull(MuteInfo)
    async def get_member_mute_info(ctx: Context, target: Selector):
        assert target is not None
        result = await ctx.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return MuteInfo(
            result.get("mutetimeRemaining") is not None,
            timedelta(seconds=(result.get("mutetimeRemaining") or 0)),
            None,
        )

    @implement(MuteTrait.mute)
    async def mute_member(ctx: Context, target: Selector, duration: timedelta):
        privilege_info = await ctx.pull(Privilege, target)
        if not privilege_info.effective:
            self_privilege_info = await ctx.pull(Privilege >> Summary, ctx.self)
            raise PermissionError(
                permission_error_message(
                    f"mute@{target.path}", self_privilege_info.name, ["group_owner", "group_admin"]
                )
            )
        time = max(0, min(int(duration.total_seconds()), 2592000))  # Fix time parameter
        if not time:
            return
        await ctx.account.call(
            "mute",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
                "time": time,
            },
        )

    @implement(MuteTrait.unmute)
    async def unmute_member(ctx: Context, target: Selector):
        privilege_info = await ctx.pull(Privilege, target)
        if not privilege_info.effective:
            self_privilege_info = await ctx.pull(Privilege >> Summary, ctx.self)
            raise PermissionError(
                permission_error_message(
                    f"unmute@{target.path}", self_privilege_info.name, ["group_owner", "group_admin"]
                )
            )
        await ctx.account.call(
            "unmute",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )

    @pull(Privilege)
    async def get_member_privilege(ctx: Context, target: Selector):
        self_info = (
            await ctx.account.call(
                "memberInfo",
                {
                    "__method__": "fetch",
                    "target": int(ctx.self.pattern["group"]),
                    "memberId": int(ctx.self.pattern["member"]),
                },
            )
        )["permission"]
        target_info = (
            await ctx.account.call(
                "memberInfo",
                {
                    "__method__": "fetch",
                    "target": int(target.pattern["group"]),
                    "memberId": int(target.pattern["member"]),
                },
            )
        )["permission"]
        return Privilege(privilege_level[self_info] > 0, privilege_level[self_info] > privilege_level[target_info])

    @pull(Privilege >> Summary)
    async def get_member_privilege_summary_info(ctx: Context, target: Selector | None) -> Summary:
        if target is None:
            self_info = await ctx.account.call(
                "memberInfo",
                {
                    "__method__": "fetch",
                    "target": int(ctx.self.pattern["group"]),
                    "memberId": int(ctx.self.pattern["member"]),
                },
            )
            return Summary(
                privilege_trans[self_info["permission"]],
                "the permission info of current account in the group",
            ).infers(Privilege >> Summary)
        target_info = await ctx.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Summary(
            privilege_trans[target_info["permission"]],
            "the permission info of current account in the group",
        ).infers(Privilege >> Summary)

    @pull(Privilege >> Privilege)
    async def get_member_privilege_of_privilege(ctx: Context, target: Selector):
        self_info = (
            await ctx.account.call(
                "memberInfo",
                {
                    "__method__": "fetch",
                    "target": int(ctx.self.pattern["group"]),
                    "memberId": int(ctx.self.pattern["member"]),
                },
            )
        )["permission"]
        return Privilege(privilege_level[self_info] == 2, privilege_level[self_info] == 2).infers(Privilege >> Summary)

    @pull(Privilege >> Privilege >> Summary)
    async def get_member_privilege_of_privilege_summary(ctx: Context, target: Selector):
        self_info = (
            await ctx.account.call(
                "memberInfo",
                {
                    "__method__": "fetch",
                    "target": int(ctx.self.pattern["group"]),
                    "memberId": int(ctx.self.pattern["member"]),
                },
            )
        )["permission"]
        return Summary(
            privilege_trans[self_info["permission"]],
            "the permission of controling administration of the group, to be noticed that is only group owner could do this.",
        ).infers(Privilege >> Privilege >> Summary)

    @implement(PrivilegeTrait.upgrade)
    async def upgrade_member(ctx: Context, target: Selector, dest: str | None = None):
        if not (await get_member_privilege_of_privilege(ctx, target)).available:
            self_privilege_info = await ctx.pull(Privilege >> Summary, ctx.self)
            raise PermissionError(
                permission_error_message(f"upgrade_permission@{target.path}", self_privilege_info.name, ["group_owner"])
            )
        await ctx.account.call(
            "memberAdmin",
            {
                "__method__": "update",
                "target": int(ctx.self.pattern["group"]),
                "memberId": int(ctx.self.pattern["member"]),
                "assign": True,
            },
        )

    @implement(PrivilegeTrait.downgrade)
    async def downgrade_member(ctx: Context, target: Selector, dest: str | None = None):
        if not (await get_member_privilege_of_privilege(ctx, target)).available:
            self_privilege_info = await ctx.pull(Privilege >> Summary, ctx.self)
            raise PermissionError(
                permission_error_message(f"upgrade_permission@{target.path}", self_privilege_info.name, ["group_owner"])
            )
        await ctx.account.call(
            "memberAdmin",
            {
                "__method__": "update",
                "target": int(ctx.self.pattern["group"]),
                "memberId": int(ctx.self.pattern["member"]),
                "assign": False,
            },
        )

    @implement(SceneTrait.remove_member)
    async def remove_member(ctx: Context, target: Selector, reason: str | None = None):
        privilege_info = await ctx.pull(Privilege, target)
        if not privilege_info.effective:
            self_privilege_info = await ctx.pull(Privilege >> Summary, ctx.self)
            raise PermissionError(
                permission_error_message(
                    f"remove@{target.path}", self_privilege_info.name, ["group_owner", "group_admin"]
                )
            )
        await ctx.account.call(
            "kick",
            {"__method__": "update", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )

    @pull(Nick)
    async def get_member_nick(ctx: Context, target: Selector) -> Nick:
        result = await ctx.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Nick(result["memberName"], result["memberName"], result.get("specialTitle"))


with bounds("group.member.nudge"):

    @implement(ActivityTrigger.trigger)
    async def send_member_nudge(ctx: Context, target: Selector):
        await ctx.account.call(
            "sendNudge",
            {"__method__": "update", "target": int(target["member"]), "subject": int(target["group"]), "kind": "Group"},
        )
