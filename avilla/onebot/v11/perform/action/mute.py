from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.privilege import MuteAllCapability, MuteCapability

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class OneBot11MuteActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.post_applying = True

    @MuteCapability.mute.collect(m, "land.group.member")
    async def mute_member(self, target: Selector, duration: timedelta):
        result = self.account.call(
            "set_group_ban",
            {
                "group_id": int(target["group"]),
                "user_id": int(target["member"]),
                "duration": int(duration.total_seconds()),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to mute {target}: {result}")

    @MuteCapability.mute.collect(m, "land.group.anonymous")
    async def mute_anonymous(self, target: Selector, duration: timedelta):
        result = self.account.call(
            "set_group_anonymous_ban",
            {
                "group_id": int(target["group"]),
                "anonymous_flag": target["anonymous"],
                "duration": int(duration.total_seconds()),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to mute {target}: {result}")

    @MuteCapability.unmute.collect(m, "land.group.member")
    async def unmute_member(self, target: Selector):
        result = self.account.call(
            "set_group_ban", {"group_id": int(target["group"]), "user_id": int(target["member"]), "duration": 0}
        )
        if result is None:
            raise RuntimeError(f"Failed to mute {target}: {result}")

    @MuteAllCapability.mute_all.collect(m, "land.group")
    async def mute_all_group(self, target: Selector):
        result = self.account.call("set_group_whole_ban", {"group_id": int(target["group"]), "enable": True})
        if result is None:
            raise RuntimeError(f"Failed to mute all {target}: {result}")

    @MuteAllCapability.unmute_all.collect(m, "land.group")
    async def unmute_all_group(self, target: Selector):
        result = self.account.call("set_group_whole_ban", {"group_id": int(target["group"]), "enable": False})
        if result is None:
            raise RuntimeError(f"Failed to unmute all {target}: {result}")
