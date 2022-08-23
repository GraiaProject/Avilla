from __future__ import annotations

from avilla.core.traitof import OrientedFn, Trait


class RequestTrait(Trait):
    @OrientedFn
    async def accept(self):
        ...

    @OrientedFn
    async def reject(self):
        ...

    @OrientedFn
    async def cancel(self):
        ...

    @OrientedFn
    async def ignore(self):
        ...
