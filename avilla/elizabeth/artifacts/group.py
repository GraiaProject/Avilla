from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.spec.core.message import MessageSend
from avilla.spec.core.privilege import MuteAllCapability, Privilege
from avilla.spec.core.profile import Summary, SummaryCapability
from avilla.spec.core.scene import SceneCapability

from avilla.core.message import Message
from avilla.core.metadata import MetadataOf
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull

if TYPE_CHECKING:
    from graia.amnesia.message import MessageChain

    from avilla.core.context import Context

    from ..protocol import ElizabethProtocol


with bounds("group"):
    # casts(MessageSend)
    # casts(MessageRevoke)
    # casts(MuteCapability)
    # casts(MuteAllCapability)
    # casts(SceneCapability)
    # casts(SummaryCapability)

    @implement(MessageSend.send)
    async def send_group_message(
        cx: Context, target: Selector, message: MessageChain, *, reply: Selector | None = None
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(cx.protocol, ElizabethProtocol)
        serialized_msg = await cx.protocol.serialize_message(message)
        result = await cx.account.call(
            "sendGroupMessage",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
                "messageChain": serialized_msg,
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        message_metadata = Message(
            id=str(result["messageId"]),
            scene=Selector().land(cx.land).group(str(target.pattern["group"])),
            content=message,
            time=datetime.now(),
            sender=Selector().land(cx.land).group(str(target.pattern["group"])).member(cx.account.id),
        )
        message_selector = message_metadata.to_selector()
        cx._collect_metadatas(message_selector, message_metadata)
        return message_selector

    @implement(MuteAllCapability.mute_all)
    async def group_mute_all(cx: Context, target: Selector):
        await cx.account.call(
            "muteAll",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
            },
        )

    @implement(MuteAllCapability.unmute_all)
    async def group_unmute_all(cx: Context, target: Selector):
        await cx.account.call(
            "unmuteAll",
            {
                "__method__": "update",
                "target": int(target.pattern["group"]),
            },
        )

    @implement(SceneCapability.leave)
    async def leave(cx: Context, target: Selector):
        await cx.account.call("quit", {"__method__": "update", "target": int(target.pattern["group"])})

    @pull(Summary)
    async def get_summary(cx: Context, target: Selector | None) -> Summary:
        assert target is not None
        result = await cx.account.call(
            "groupConfig",
            {"__method__": "fetch", "target": int(target.pattern["group"])},
        )
        return Summary(name=result["name"], description=None)

    @implement(SummaryCapability.set_name)
    async def group_set_name(cx: Context, target: Selector | MetadataOf, name: str):
        SummaryCapability.set_name.assert_entity(target)
        if TYPE_CHECKING:
            assert isinstance(target, Selector)
        await cx.account.call(
            "groupConfig",
            {"__method__": "update", "target": int(target.pattern["group"]), "config": {"name": name}},
        )

    @pull(Privilege)
    async def group_get_privilege_info(cx: Context, target: Selector | None) -> Privilege:
        self_info = await cx.account.call(
            "memberInfo",
            {
                "__method__": "fetch",
                "target": int(cx.self.pattern["group"]),
                "memberId": int(cx.self.pattern["member"]),
            },
        )
        if target is None:
            return Privilege(
                self_info["permission"] in {"OWNER", "ADMINISTRATOR"},
                self_info["permission"] in {"OWNER", "ADMINISTRATOR"},
            )
        target_info = await cx.account.call(
            "memberInfo",
            {"__method__": "fetch", "target": int(target.pattern["group"]), "memberId": int(target.pattern["member"])},
        )
        return Privilege(
            self_info["permission"] in {"OWNER", "ADMINISTRATOR"},
            (self_info["permission"] == "OWNER" and target_info["permission"] != "OWNER")
            or (
                self_info["permission"] in {"OWNER", "ADMINISTRATOR"}
                and target_info["permission"] not in {"OWNER", "ADMINISTRATOR"}
            ),
        )
