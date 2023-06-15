from __future__ import annotations

from datetime import timedelta

from avilla.core.ryanvk import Capability, TargetFn
from avilla.core.selector import Selector


class PrivilegeCapability(Capability):
    @TargetFn
    async def upgrade(self, target: Selector, dest: str | None = None) -> None:
        ...

    @TargetFn
    async def downgrade(self, target: Selector, dest: str | None = None) -> None:
        ...


class MuteCapability(Capability):
    @TargetFn
    async def mute(self, target: Selector, duration: timedelta) -> None:
        ...

    @TargetFn
    async def unmute(self, target: Selector) -> None:
        ...


class MuteAllCapability(Capability):
    @TargetFn
    async def mute_all(self, target: Selector) -> None:
        ...

    @TargetFn
    async def unmute_all(self, target: Selector) -> None:
        ...

    # Fetch => rs.pull(MuteInfo, target=...)


class BanCapability(Capability):
    @TargetFn
    async def ban(self, target: Selector, *, duration: timedelta | None = None, reason: str | None = None) -> None:
        ...

    @TargetFn
    async def unban(self, target: Selector) -> None:
        ...
