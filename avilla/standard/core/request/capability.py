from __future__ import annotations

from avilla.core.ryanvk import Capability, Fn, TargetOverload
from avilla.core.selector import Selector


class RequestCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def accept(self, target: Selector):
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def reject(self, target: Selector, reason: str | None = None, forever: bool = False):
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def cancel(self, target: Selector):
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def ignore(self, target: Selector):
        ...
