from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.privilege import PrivilegeCapability

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
