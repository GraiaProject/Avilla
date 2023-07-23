from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.builtins.capability import CoreCapability
from avilla.core.exceptions import permission_error_message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.elizabeth.const import PRIVILEGE_LEVEL
from avilla.standard.core.privilege import MuteAllCapability, Privilege
from avilla.standard.core.profile import Summary, SummaryCapability
from avilla.standard.core.relation import SceneCapability

if TYPE_CHECKING:
    from avilla.elizabeth.account import ElizabethAccount  # noqa
    from avilla.elizabeth.protocol import ElizabethProtocol  # noqa


class ElizabethGroupActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @m.pull("land.group", Summary)
    async def get_summary(self, target: Selector) -> Summary:
        result = await self.account.connection.call(
            "fetch",
            "groupConfig",
            {
                "target": int(target.pattern["group"]),
            },
        )
        return Summary(result["name"], None)

    @MuteAllCapability.mute_all.collect(m, "land.group")
    async def group_mute_all(self, target: Selector):
        await self.account.connection.call(
            "update",
            "muteAll",
            {
                "target": int(target.pattern["group"]),
            },
        )

    @MuteAllCapability.unmute_all.collect(m, "land.group")
    async def group_unmute_all(self, target: Selector):
        await self.account.connection.call(
            "update",
            "unmuteAll",
            {
                "target": int(target.pattern["group"]),
            },
        )

    @SceneCapability.leave.collect(m, "land.group")
    async def group_leave(self, target: Selector):
        await self.account.connection.call(
            "update",
            "quit",
            {
                "target": int(target.pattern["group"]),
            },
        )

    @SummaryCapability.set_name.collect(m, "land.group", Summary)
    async def group_set_name(self, target: Selector, t: ..., name: str):
        privilege_info = await self.account.staff.pull_metadata(target, Privilege)
        if not privilege_info.available:
            self_permission = await self.account.staff.pull_metadata(
                target.into(f"~.member({self.account.route['account']})"), Privilege >> Summary
            )
            raise PermissionError(
                permission_error_message(
                    f"set_name@{target.path}", self_permission.name, ["group_owner", "group_admin"]
                )
            )
        await self.account.connection.call(
            "update",
            "groupConfig",
            {
                "target": int(target.pattern["group"]),
                "config": {
                    "name": name,
                },
            },
        )

    @CoreCapability.pull.collect(m, "land.group", Privilege)
    async def group_get_privilege_info(self, target: Selector) -> Privilege:
        self_info = await self.account.connection.call(
            "fetch",
            "memberInfo",
            {
                "target": int(target.pattern["group"]),
                "memberId": int(self.account.route["account"]),
            },
        )
        return Privilege(
            PRIVILEGE_LEVEL[self_info["permission"]] > 0,
            PRIVILEGE_LEVEL[self_info["permission"]] > 0,
        )
