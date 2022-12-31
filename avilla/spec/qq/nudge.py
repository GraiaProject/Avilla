from __future__ import annotations

from avilla.core.trait import Fn, Trait

class QQNudge(Trait):
    @Fn.bound_entity
    async def nudge(self):
        ...