from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.privilege import PrivilegeCapability, Privilege
from avilla.standard.core.profile import Summary
from ...utils import PRIVILEGE_LEVEL, PRIVILEGE_TRANS

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class OneBot11PrivilegeActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::action"
    m.identify = "admin"

    @PrivilegeCapability.upgrade.collect(m, target="land.group.member")
    async def upgrade_perm(self, target: Selector, dest: str | None = None):
        result = await self.account.connection.call(
            "set_group_admin", {"group_id": int(target["group"]), "user_id": int(target["member"]), "enable": True}
        )
        if result is not None:
            raise RuntimeError(f"Failed to upgrade permission to {target}: {result}")

    @PrivilegeCapability.downgrade.collect(m, target="land.group.member")
    async def downgrade_perm(self, target: Selector, dest: str | None = None):
        result = await self.account.connection.call(
            "set_group_admin", {"group_id": int(target["group"]), "user_id": int(target["member"]), "enable": False}
        )
        if result is not None:
            raise RuntimeError(f"Failed to downgrade permission to {target}: {result}")

    @m.pull("land.group.member", Privilege)
    async def get_group_member_privilege(self, target: Selector, route: ...) -> Privilege:
        if target.pattern["member"] == self.account.route["account"]:
            return Privilege(True, True)
        self_info = await self.account.connection.call(
            "get_group_member_info ",
            {"group_id": int(target["group"]), "user_id": int(self.account.route["account"])},
        )
        if self_info is None:
            raise RuntimeError(f"Failed to get self info in {target}")
        target_info = await self.account.connection.call(
            "get_group_member_info ",
            {"group_id": int(target["group"]), "user_id": int(target.pattern["member"])},
        )
        if target_info is None:
            raise RuntimeError(f"Failed to get target info in {target}")
        return Privilege(
            PRIVILEGE_LEVEL[target_info["role"]] > 0,
            PRIVILEGE_LEVEL[self_info["role"]] > PRIVILEGE_LEVEL[target_info["role"]],
        )

    @m.pull("land.group.member", Privilege >> Summary)
    async def get_group_member_privilege_summary(self, target: Selector, route: ...) -> Summary:
        target_info = await self.account.connection.call(
            "get_group_member_info",
            {"group_id": int(target["group"]), "user_id": int(target.pattern["member"])},
        )
        if target_info is None:
            raise RuntimeError(f"Failed to get target info in {target}")
        return Summary(
            PRIVILEGE_TRANS[target_info["role"]], "the permission info of current account in the group"
        ).infers(Privilege >> Summary)

    @m.pull("land.group.member", Privilege >> Privilege)
    async def get_group_member_privilege_privilege(self, target: Selector, route: ...) -> Privilege:
        self_info = await self.account.connection.call(
            "get_group_member_info",
            {"group_id": int(target["group"]), "user_id": int(self.account.route["account"])},
        )
        if self_info is None:
            raise RuntimeError(f"Failed to get self info in {target}")
        result = await self.account.connection.call(
            "get_group_member_info",
            {"group_id": int(target["group"]), "user_id": int(target.pattern["member"])},
        )
        if result is None:
            raise RuntimeError(f"Failed to get target info in {target}")
        return Privilege(
            PRIVILEGE_LEVEL[result["role"]] == 2,
            PRIVILEGE_LEVEL[self_info["role"]] > PRIVILEGE_LEVEL[result["role"]],
        ).infers(Privilege >> Privilege)

    @m.pull("land.group.member", Privilege >> Privilege >> Summary)
    async def get_group_member_privilege_privilege_summary(self, target: Selector, route: ...) -> Summary:
        target_info = await self.account.connection.call(
            "get_group_member_info",
            {"group_id": int(target["group"]), "user_id": int(target.pattern["member"])},
        )
        if target_info is None:
            raise RuntimeError(f"Failed to get target info in {target}")
        return Summary(
            PRIVILEGE_TRANS[target_info["role"]],
            "the permission of controling administration of the group,"
            "to be noticed that is only group owner could do this.",
        ).infers(Privilege >> Privilege >> Summary)

    @m.pull("land.group", Privilege)
    async def group_get_privilege_info(self, target: Selector, route: ...) -> Privilege:
        self_info = await self.account.connection.call(
            "get_group_member_info",
            {"group_id": int(target["group"]), "user_id": int(self.account.route["account"])},
        )
        if self_info is None:
            raise RuntimeError(f"Failed to get self info in {target}")
        return Privilege(
            PRIVILEGE_LEVEL[self_info["role"]] > 0,
            PRIVILEGE_LEVEL[self_info["role"]] > 0,
        )
