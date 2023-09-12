from __future__ import annotations

from avilla.core.ryanvk import Capability, Fn, TargetOverload
from avilla.core.selector import Selector


class ActivityTrigger(Capability):
    @Fn.custom({TargetOverload(): ["target"]})
    async def trigger(self, target: Selector):
        ...
