from __future__ import annotations

from avilla.core.traitof import OrientedFn, Trait


class SummaryTrait(Trait):
    @OrientedFn
    async def set_name(self, name: str) -> None:
        ...

    @OrientedFn
    async def unset_name(self) -> None:
        ...

    @OrientedFn
    async def set_description(self, description: str) -> None:
        ...

    @OrientedFn
    async def unset_description(self) -> None:
        ...
