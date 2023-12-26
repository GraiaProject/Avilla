from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.privilege import BanCapability

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class OneBot11BanActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::action"
    m.identify = "ban"

    @BanCapability.ban.collect(m, target="land.group.member")
    async def ban_member(self, target: Selector, *, duration: timedelta | None = None, reason: str | None = None):
        result = await self.account.connection.call(
            "set_group_kick",
            {
                "group_id": int(target["group"]),
                "user_id": int(target["member"]),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to ban {target}: {result}")
