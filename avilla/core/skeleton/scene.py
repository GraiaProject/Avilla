from __future__ import annotations

from avilla.core.trait import Fn, Trait, TBounded
from avilla.core.utilles.selector import Selector


class SceneTrait(Trait[TBounded]):
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
