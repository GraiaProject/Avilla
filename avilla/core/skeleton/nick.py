from __future__ import annotations

from avilla.core.trait import Fn, OrientedFn, Trait
from avilla.core.utilles.selector import Selector


class NickTrait(Trait):
    @OrientedFn
    async def set_name(self, name: str) -> None:
        ...

    @OrientedFn
    async def set_nickname(self, nickname: str) -> None:
        ...

    @OrientedFn
    async def unset_nickname(self) -> None:
        ...

    # TODO: recheck badge operators

    @Fn
    async def set_badge(self, target: Selector, badge: str) -> None:
        ...

    @Fn
    async def unset_badge(self, target: Selector) -> None:
        ...
