from __future__ import annotations

from avilla.core.ryanvk import Capability, TargetFn


class SceneCapability(Capability):
    @TargetFn
    async def leave(self) -> None:
        ...

    @TargetFn
    async def disband(self) -> None:
        ...

    @TargetFn
    async def remove_member(self, reason: str | None = None) -> None:
        ...

    # TODO: join, invite etc.
