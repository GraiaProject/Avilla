from avilla.core.trait import Fn, Trait


class ActivityTrigger(Trait):
    @Fn.bound_entity
    async def trigger(self):
        ...
