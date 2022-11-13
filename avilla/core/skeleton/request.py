from __future__ import annotations

from avilla.core.abstract.trait import Fn, TBounded, Trait


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
