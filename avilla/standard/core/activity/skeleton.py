from avilla.core.ryanvk import Capability, TargetFn


class ActivityTrigger(Capability):
    @TargetFn
    async def trigger(self):
        ...
