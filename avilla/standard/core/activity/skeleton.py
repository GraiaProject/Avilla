from avilla.core.ryanvk import Capability, TargetFn

from avilla.core.selector import Selector

class ActivityTrigger(Capability):
    @TargetFn
    async def trigger(self, target: Selector):
        ...
