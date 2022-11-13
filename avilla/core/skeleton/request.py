from __future__ import annotations

from avilla.core.trait import Fn, Trait, TBounded


class RequestTrait(Trait[TBounded]):
    @Fn.bound
    async def accept(self):
        ...

    @Fn.bound
    async def reject(self, reason: str | None = None, forever: bool = False):
        ...

    @Fn.bound
    async def cancel(self):
        ...

    @Fn.bound
    async def ignore(self):
        ...
