from __future__ import annotations

from avilla.core.trait import Fn, Trait


class RequestTrait(Trait):
    @Fn.bound_entity
    async def accept(self):
        ...

    @Fn.bound_entity
    async def reject(self, reason: str | None = None, forever: bool = False):
        ...

    @Fn.bound_entity
    async def cancel(self):
        ...

    @Fn.bound_entity
    async def ignore(self):
        ...
