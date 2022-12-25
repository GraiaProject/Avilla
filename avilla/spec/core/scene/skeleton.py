from __future__ import annotations

from avilla.core.trait import Fn, Trait


class SceneTrait(Trait):
    @Fn.bound_entity
    async def leave(self) -> None:
        ...

    @Fn.bound_entity
    async def disband(self) -> None:
        ...

    @Fn.bound_entity
    async def remove_member(self, reason: str | None = None) -> None:
        ...

    # TODO: join, invite etc.
