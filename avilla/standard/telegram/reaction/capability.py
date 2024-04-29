from __future__ import annotations

from avilla.core import Selector
from avilla.core.ryanvk import TargetOverload
from graia.ryanvk import Capability, Fn


class ReactionCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def set(self, target: Selector, emoji: list[str], is_big: bool | None = None) -> None: ...
