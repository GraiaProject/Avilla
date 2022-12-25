from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from avilla.core.exceptions import permission_error_message
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull
from avilla.spec.core.privilege import MuteAllTrait, MuteTrait, Privilege
from avilla.spec.core.profile import Nick, Summary

from ...core.metadata import MetadataOf
from ...spec.core.scene.skeleton import SceneTrait

if TYPE_CHECKING:
    from graia.amnesia.message import __message_chain_class__

    from avilla.core.context import Context

    from ..protocol import ElizabethProtocol


privilege_trans = defaultdict(lambda: "group_member", {"OWNER": "group_owner", "ADMINISTRATOR": "group_admin"})
privilege_level = defaultdict(lambda: 0, {"OWNER": 2, "ADMINISTRATOR": 1})

with bounds("group.member"):

    @implement(MuteTrait.mute)
    async def mute_member(ctx: Context, target: Selector, duration: timedelta):
        privilege_info = await ctx.pull(Privilege, target)
        if not privilege_info.effective:
            self_privilege_info = await ctx.pull(Privilege >> Summary, ctx.self)
            raise PermissionError(
                permission_error_message(
                    f"Mute.mute@{target.path}", self_privilege_info.name, ["group_owner", "group_admin"]
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
                    f"Mute.unmute@{target.path}", self_privilege_info.name, ["group_owner", "group_admin"]
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
    async def group_member_get_privilege(ctx: Context, target: Selector):
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
        return Privilege(
            Privilege, privilege_level[self_info] > 0, privilege_level[self_info] > privilege_level[target_info]
        )

    @pull(Privilege >> Summary)
    async def group_member_get_privilege_summary_info(ctx: Context, target: Selector | None) -> Summary:
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
                Privilege >> Summary,
                privilege_trans[self_info["permission"]],
                "the permission info of current account in the group",
            )
        target_info = await ctx.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Summary(
            Privilege >> Summary,
            privilege_trans[target_info["permission"]],
            "the permission info of current account in the group",
        )

    @implement(SceneTrait.remove_member)
    async def remove_member(ctx: Context, target: Selector, reason: str | None = None):
        privilege_info = await ctx.pull(Privilege, target)
        if not privilege_info.effective:
            raise PermissionError()  # TODO: error message, including Summary info
        await ctx.account.call(
            "kick",
            {"__method__": "update", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )

    @pull(Nick)
    async def get_member_nick(ctx: Context, target: Selector | None) -> Nick:
        assert target is not None
        result = await ctx.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Nick(Nick, result["memberName"], result["memberName"], result["specialTitle"])
