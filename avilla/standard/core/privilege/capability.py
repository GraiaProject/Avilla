from __future__ import annotations

from datetime import timedelta

from avilla.core.ryanvk import Capability, TargetOverload, Fn
from avilla.core.selector import Selector


class PrivilegeCapability(Capability):
    @Fn.with_overload({TargetOverload(): ["target"]})
    async def upgrade(self, target: Selector, dest: str | None = None) -> None:
        ...

    @Fn.with_overload({TargetOverload(): ["target"]})
    async def downgrade(self, target: Selector, dest: str | None = None) -> None:
        ...


class MuteCapability(Capability):
    @Fn.with_overload({TargetOverload(): ["target"]})
    async def mute(self, target: Selector, duration: timedelta) -> None:
        ...

    @Fn.with_overload({TargetOverload(): ["target"]})
    async def unmute(self, target: Selector) -> None:
        ...


class MuteAllCapability(Capability):
    @Fn.with_overload({TargetOverload(): ["target"]})
    async def mute_all(self, target: Selector) -> None:
        ...

    @Fn.with_overload({TargetOverload(): ["target"]})
    async def unmute_all(self, target: Selector) -> None:
        ...

    # Fetch => rs.pull(MuteInfo, target=...)


class BanCapability(Capability):
    @Fn.with_overload({TargetOverload(): ["target"]})
    async def ban(self, target: Selector, *, duration: timedelta | None = None, reason: str | None = None) -> None:
        ...

    @Fn.with_overload({TargetOverload(): ["target"]})
    async def unban(self, target: Selector) -> None:
        ...
