from __future__ import annotations

from avilla.core.ryanvk import Capability, TargetFn


class NudgeCapability(Capability):
    @TargetFn
    async def nudge(self):
        ...


# TODO: other qq capabilities
