from __future__ import annotations

from avilla.core.traitof import Fn, OrientedFn, Trait


class SceneTrait(Trait):
    @OrientedFn
    async def leave(self) -> None:
        ...

    @OrientedFn
    async def disband(self) -> None:
        ...

    @Fn
    async def remove_member(self) -> None:
        ...
    # TODO: join, invite etc.
