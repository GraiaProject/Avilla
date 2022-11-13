from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import TYPE_CHECKING

from avilla.core.abstract.trait.context import prefix, raise_for_no_namespace, scope
from avilla.core.abstract.trait.recorder import casts, default_target, impl, pull, query
from avilla.core.exceptions import permission_error_message
from avilla.core.message import Message
from avilla.core.metadata.cells import Nick, Privilege, Summary
from avilla.core.skeleton.message import MessageRevoke, MessageSend
from avilla.core.skeleton.privilege import MuteAllTrait, MuteTrait
from avilla.core.skeleton.scene import SceneTrait
from avilla.core.skeleton.summary import SummaryTrait
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from graia.amnesia.message import MessageChain

    from avilla.core.context import Context

raise_for_no_namespace()

with scope("qq", "group"), prefix("group"):

    casts(MessageSend)
    casts(MessageRevoke)
    casts(MuteTrait)
    casts(MuteAllTrait)
    casts(SceneTrait)
    casts(SummaryTrait)

    @default_target(MessageSend.send)
    def send_group_message_default_target(rs: Context):
        return rs.scene

    @impl(MessageSend.send)
    async def send_group_message(
        rs: Context, target: Selector, message: MessageChain, *, reply: Selector | None = None
    ) -> Selector:
        serialized_msg = await rs.protocol.serialize_message(message)
        result = await rs.account.call(
            "sendGroupMessage",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
                "messageChain": serialized_msg,
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        return Selector().land(rs.land).group(target.pattern["group"]).message(result["messageId"])

    @impl(MessageRevoke.revoke)
    async def revoke_group_message(rs: Context, message: Selector):
        await rs.account.call(
            "recall",
            {
                "__method__": "update",
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["group"]),
            },
        )

    @impl(MuteTrait.mute)
    async def mute_member(rs: Context, target: Selector, duration: timedelta):
        privilege_info = await rs.pull(Privilege, target)
        if not privilege_info.effective:
            self_privilege_info = await rs.pull(Privilege >> Summary, rs.self)
            raise PermissionError(
                permission_error_message(
                    f"Mute.mute@{target.path}", self_privilege_info.name, ["group_owner", "group_admin"]
                )
            )
        time = max(0, min(int(duration.total_seconds()), 2592000))  # Fix time parameter
        if not time:
            return
        await rs.account.call(
            "mute",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
                "time": time,
            },
        )

    @impl(MuteTrait.unmute)
    async def unmute_member(rs: Context, target: Selector):
        privilege_info = await rs.pull(Privilege, target)
        if not privilege_info.effective:
            self_privilege_info = await rs.pull(Privilege >> Summary, rs.self)
            raise PermissionError(
                permission_error_message(
                    f"Mute.unmute@{target.path}", self_privilege_info.name, ["group_owner", "group_admin"]
                )
            )
        await rs.account.call(
            "unmute",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
                "memberId": int(target.pattern["member"]),
            },
        )

    @impl(MuteAllTrait.mute_all)
    async def group_mute_all(rs: Context, target: Selector):
        await rs.account.call(
            "muteAll",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
            },
        )

    @impl(MuteAllTrait.unmute_all)
    async def group_unmute_all(rs: Context, target: Selector):
        await rs.account.call(
            "unmuteAll",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
            },
        )

    @impl(SceneTrait.leave).pin("group")
    async def leave(rs: Context, target: Selector):
        await rs.account.call("quit", {"__method__": "update", "target": int(target.pattern["group"])})

    @impl(SceneTrait.remove_member)
    async def remove_member(rs: Context, target: Selector, reason: str | None = None):
        privilege_info = await rs.pull(Privilege, target)
        if not privilege_info.effective:
            raise PermissionError()  # TODO: error message, including Summary info
        await rs.account.call(
            "kick",
            {"__method__": "update", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )

    @pull(Summary).of("group")
    async def get_summary(rs: Context, target: Selector | None) -> Summary:
        assert target is not None
        result = await rs.account.call(
            "groupConfig",
            {"__method__": "fetch", "target": int(target.pattern["group"])},
        )
        return Summary(describe=Summary, name=result["name"], description=None)

    @impl(SummaryTrait.set_name).pin("group")
    async def group_set_name(rs: Context, target: Selector, name: str):
        await rs.account.call(
            "groupConfig",
            {"__method__": "update", "target": int(target.pattern["group"]), "config": {"name": name}},
        )

    @pull(Privilege).of("group.member")
    async def group_get_privilege_info(rs: Context, target: Selector | None) -> Privilege:
        self_info = await rs.account.call(
            "memberInfo",
            {
                "__method__": "fetch",
                "target": int(rs.self.pattern["group"]),
                "memberId": int(rs.self.pattern["member"]),
            },
        )
        if target is None:
            return Privilege(
                Privilege,
                self_info["permission"] in {"OWNER", "ADMINISTRATOR"},
                self_info["permission"] in {"OWNER", "ADMINISTRATOR"},
            )
        target_info = await rs.account.call(
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

    @pull(Privilege >> Summary).of("group.member")
    async def group_get_privilege_summary_info(rs: Context, target: Selector | None) -> Summary:
        privilege_trans = defaultdict(lambda: "group_member", {"OWNER": "group_owner", "ADMINISTRATOR": "group_admin"})

        if target is None:
            self_info = await rs.account.call(
                "memberInfo",
                {
                    "__method__": "fetch",
                    "target": int(rs.self.pattern["group"]),
                    "memberId": int(rs.self.pattern["member"]),
                },
            )
            return Summary(
                Privilege >> Summary,
                privilege_trans[self_info["permission"]],
                "the permission info of current account in the group",
            )
        target_info = await rs.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Summary(
            Privilege >> Summary,
            privilege_trans[target_info["permission"]],
            "the permission info of current account in the group",
        )

    @pull(Nick).of("group.member")
    async def get_member_nick(rs: Context, target: Selector | None) -> Nick:
        assert target is not None
        result = await rs.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Nick(Nick, result["memberName"], result["memberName"], result["specialTitle"])

    @query(None, "group")
    async def get_groups(rs: Context, upper: None, predicate: Selector):
        result: list[dict] = await rs.account.call("groupList", {"__method__": "fetch"})
        for i in result:
            group = Selector().group(str(i["id"]))
            if predicate.match(group):
                yield group

    @query("group", "member")
    async def get_group_members(rs: Context, upper: Selector, predicate: Selector):
        result: list[dict] = await rs.account.call(
            "memberList", {"__method__": "fetch", "target": int(upper.pattern["group"])}
        )
        for i in result:
            member = Selector().group(str(i["group"]["id"])).member(str(i["id"]))
            if predicate.match(member):
                yield member
