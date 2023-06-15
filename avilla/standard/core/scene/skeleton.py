from __future__ import annotations

from avilla.core.ryanvk import TargetFn, Capability


class SceneCapabilty(Capability):
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
