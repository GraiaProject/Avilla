from __future__ import annotations

from avilla.core.trait import Fn, Trait, TBounded


class SummaryTrait(Trait[TBounded]):
    @Fn.bound
    async def set_name(self, name: str) -> None:
        ...

    @Fn.bound
    async def unset_name(self) -> None:
        ...

    @Fn.bound
    async def set_description(self, description: str) -> None:
        ...

    @Fn.bound
    async def unset_description(self) -> None:
        ...
