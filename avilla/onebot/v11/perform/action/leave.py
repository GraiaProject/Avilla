from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.relation import SceneCapability

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class OneBot11LeaveActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.post_applying = True

    @SceneCapability.leave.collect(m, "land.group")
    async def leave_group(self, target: Selector):
        result = self.account.call("set_group_leave", {"group_id": int(target["group"])})
        if result is None:
            raise RuntimeError(f"Failed to leave group: {target}: {result}")

    @SceneCapability.disband.collect(m, "land.group")
    async def disband_group(self, target: Selector):
        result = self.account.call("set_group_leave", {"group_id": int(target["group"]), "is_dismiss": True})
        if result is None:
            raise RuntimeError(f"Failed to disband group: {target}: {result}")
