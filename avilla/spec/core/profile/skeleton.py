from __future__ import annotations

from avilla.core.trait import Fn, Trait


class SummaryTrait(Trait):
    @Fn.bound_universal
    async def set_name(self, name: str) -> None:
        ...

    @Fn.bound_universal
    async def unset_name(self) -> None:
        ...

    @Fn.bound_universal
    async def set_description(self, description: str) -> None:
        ...

    @Fn.bound_universal
    async def unset_description(self) -> None:
        ...


class NickTrait(Trait):
    @Fn.bound_universal
    async def set_name(self, name: str) -> None:
        ...

    @Fn.bound_entity
    async def set_nickname(self, nickname: str) -> None:
        ...

    @Fn.bound_entity
    async def unset_nickname(self) -> None:
        ...

    @Fn.bound_entity
    async def set_badge(self, badge: str) -> None:
        ...

    @Fn.bound_entity
    async def unset_badge(self) -> None:
        ...
