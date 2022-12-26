from avilla.core.trait import Trait, Fn

class ActivityTrigger(Trait):
    @Fn.bound_entity
    async def trigger(self):
        ...
