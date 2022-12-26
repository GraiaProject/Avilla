from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull
from avilla.spec.core.message import MessageSend
from avilla.spec.core.privilege import MuteAllTrait, Privilege
from avilla.spec.core.profile import Summary, SummaryTrait
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
