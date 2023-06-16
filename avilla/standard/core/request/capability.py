from __future__ import annotations

from avilla.core.ryanvk import Capability, TargetFn


class RequestCapability(Capability):
    @TargetFn
    async def accept(self):
        ...

    @TargetFn
    async def reject(self, reason: str | None = None, forever: bool = False):
        ...

    @TargetFn
    async def cancel(self):
        ...

    @TargetFn
    async def ignore(self):
        ...
