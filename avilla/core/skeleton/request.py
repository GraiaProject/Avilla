from __future__ import annotations

from avilla.core.traitof import OrientedFn, Trait


class RequestTrait(Trait):
    @OrientedFn
    async def accept(self):
        ...

    @OrientedFn
    async def reject(self, reason: str | None = None, forever: bool = False):
        ...

    @OrientedFn
    async def cancel(self):
        ...

    @OrientedFn
    async def ignore(self):
        ...
