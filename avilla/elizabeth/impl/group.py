from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from avilla.core.exceptions import permission_error_message
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull
from avilla.spec.core.message import MessageRevoke, MessageSend
from avilla.spec.core.privilege import MuteAllTrait, MuteTrait, Privilege
from avilla.spec.core.profile import Nick, Summary, SummaryTrait
from avilla.spec.core.scene import SceneTrait

from ...core.metadata import MetadataOf

if TYPE_CHECKING:
    from graia.amnesia.message import __message_chain_class__

    from avilla.core.context import Context

    from ..protocol import ElizabethProtocol


with bounds("group"):

    # casts(MessageSend)
    # casts(MessageRevoke)
    # casts(MuteTrait)
    # casts(MuteAllTrait)
    # casts(SceneTrait)
    # casts(SummaryTrait)

    @implement(MessageSend.send)
    async def send_group_message(
        ctx: Context, target: Selector, message: __message_chain_class__, *, reply: Selector | None = None
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(ctx.protocol, ElizabethProtocol)
        serialized_msg = await ctx.protocol.serialize_message(message)
        result = await ctx.account.call(
            "sendGroupMessage",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
                "messageChain": serialized_msg,
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        message_metadata = Message(
            describe=Message,
            id=str(result["messageId"]),
            scene=Selector().land(ctx.land).group(str(target.pattern["group"])),
            content=message,
            time=datetime.now(),
            sender=Selector().land(ctx.land).group(str(target.pattern["group"])).member(ctx.account.id),
        )
        message_selector = message_metadata.to_selector()
        ctx._collect_metadatas(message_selector, message_metadata)
        return message_selector

    @implement(MessageRevoke.revoke)
    async def revoke_group_message(ctx: Context, message: Selector):
        await ctx.account.call(
            "recall",
            {
                "__method__": "update",
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["group"]),
            },
        )

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

    @implement(MuteAllTrait.mute_all)
    async def group_mute_all(ctx: Context, target: Selector):
        await ctx.account.call(
            "muteAll",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
            },
        )

    @implement(MuteAllTrait.unmute_all)
    async def group_unmute_all(ctx: Context, target: Selector):
        await ctx.account.call(
            "unmuteAll",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
            },
        )

    @implement(SceneTrait.leave)
    async def leave(ctx: Context, target: Selector):
        await ctx.account.call("quit", {"__method__": "update", "target": int(target.pattern["group"])})

    @implement(SceneTrait.remove_member)
    async def remove_member(ctx: Context, target: Selector, reason: str | None = None):
        privilege_info = await ctx.pull(Privilege, target)
        if not privilege_info.effective:
            raise PermissionError()  # TODO: error message, including Summary info
        await ctx.account.call(
            "kick",
            {"__method__": "update", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )

    @pull(Summary)
    async def get_summary(ctx: Context, target: Selector | None) -> Summary:
        assert target is not None
        result = await ctx.account.call(
            "groupConfig",
            {"__method__": "fetch", "target": int(target.pattern["group"])},
        )
        return Summary(describe=Summary, name=result["name"], description=None)

    @implement(SummaryTrait.set_name)
    async def group_set_name(ctx: Context, target: Selector | MetadataOf, name: str):
        SummaryTrait.set_name.assert_entity(target)
        if TYPE_CHECKING:
            assert isinstance(target, Selector)
        await ctx.account.call(
            "groupConfig",
            {"__method__": "update", "target": int(target.pattern["group"]), "config": {"name": name}},
        )

    @pull(Privilege)
    async def group_get_privilege_info(ctx: Context, target: Selector | None) -> Privilege:
        self_info = await ctx.account.call(
            "memberInfo",
            {
                "__method__": "fetch",
                "target": int(ctx.self.pattern["group"]),
                "memberId": int(ctx.self.pattern["member"]),
            },
        )
        if target is None:
            return Privilege(
                Privilege,
                self_info["permission"] in {"OWNER", "ADMINISTRATOR"},
                self_info["permission"] in {"OWNER", "ADMINISTRATOR"},
            )
        target_info = await ctx.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Privilege(
            Privilege,
            self_info["permission"] in {"OWNER", "ADMINISTRATOR"},
            (self_info["permission"] == "OWNER" and target_info["permission"] != "OWNER")
            or (
                self_info["permission"] in {"OWNER", "ADMINISTRATOR"}
                and target_info["permission"] not in {"OWNER", "ADMINISTRATOR"}
            ),
        )


with bounds("group.member"):

    @pull(Privilege >> Summary)
    async def group_get_privilege_summary_info(ctx: Context, target: Selector | None) -> Summary:
        privilege_trans = defaultdict(lambda: "group_member", {"OWNER": "group_owner", "ADMINISTRATOR": "group_admin"})

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

    @pull(Nick)
    async def get_member_nick(ctx: Context, target: Selector | None) -> Nick:
        assert target is not None
        result = await ctx.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Nick(Nick, result["memberName"], result["memberName"], result["specialTitle"])


"""
    @query(None, "group")
    async def get_groups(ctx: Context, upper: None, predicate: Selector):
        result: list[dict] = await ctx.account.call("groupList", {"__method__": "fetch"})
        for i in result:
            group = Selector().group(str(i["id"]))
            if predicate.match(group):
                yield group

    @query("group", "member")
    async def get_group_members(ctx: Context, upper: Selector, predicate: Selector):
        result: list[dict] = await ctx.account.call(
            "memberList", {"__method__": "fetch", "target": int(upper.pattern["group"])}
        )
        for i in result:
            member = Selector().group(str(i["group"]["id"])).member(str(i["id"]))
            if predicate.match(member):
                yield member
"""
