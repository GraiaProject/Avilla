from __future__ import annotations

from avilla.core.abstract.trait import Fn, TBounded, Trait
from avilla.core.utilles.selector import Selector


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


class NickTrait(Trait[TBounded]):
    @Fn.bound
    async def set_name(self, name: str) -> None:
        ...

    @Fn.bound
    async def set_nickname(self, nickname: str) -> None:
        ...

    @Fn.bound
    async def unset_nickname(self) -> None:
        ...

    # TODO: recheck badge operators

    @Fn.bound
    async def set_badge(self, badge: str) -> None:
        ...

    @Fn.bound
    async def unset_badge(self) -> None:
        ...
