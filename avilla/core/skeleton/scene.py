from __future__ import annotations

from avilla.core.traitof import Fn, OrientedFn, Trait
from avilla.core.utilles.selector import Selector


class SceneTrait(Trait):
    @OrientedFn
    async def leave(self) -> None:
        ...

    @OrientedFn
    async def disband(self) -> None:
        ...

    @Fn
    async def remove_member(self, target: Selector, reason: str | None = None) -> None:
        ...

    # TODO: join, invite etc.
