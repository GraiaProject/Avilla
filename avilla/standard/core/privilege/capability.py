from __future__ import annotations

from datetime import timedelta

from avilla.core.ryanvk import Capability, TargetFn


class PrivilegeCapability(Capability):
    @TargetFn
    async def upgrade(self, dest: str | None = None) -> None:
        ...

    @TargetFn
    async def downgrade(self, dest: str | None = None) -> None:
        ...


class MuteCapability(Capability):
    @TargetFn
    async def mute(self, duration: timedelta) -> None:
        ...

    @TargetFn
    async def unmute(self) -> None:
        ...


class MuteAllCapability(Capability):
    @TargetFn
    async def mute_all(self) -> None:
        ...

    @TargetFn
    async def unmute_all(self) -> None:
        ...

    # Fetch => rs.pull(MuteInfo, target=...)


class BanCapability(Capability):
    @TargetFn
    async def ban(self, *, duration: timedelta | None = None, reason: str | None = None) -> None:
        ...

    @TargetFn
    async def unban(self) -> None:
        ...
