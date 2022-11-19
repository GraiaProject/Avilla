from __future__ import annotations

from avilla.core.abstract.trait import Fn, Trait
from avilla.core.utilles.selector import Selector


class SceneTrait(Trait):
    @Fn.bound
    async def leave(self) -> None:
        ...

    @Fn.bound
    async def disband(self) -> None:
        ...

    @Fn.bound
    async def remove_member(self, reason: str | None = None) -> None:
        ...

    # TODO: join, invite etc.
