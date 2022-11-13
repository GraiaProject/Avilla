from __future__ import annotations

from avilla.core.trait import Fn, Trait, TBounded
from avilla.core.utilles.selector import Selector

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
