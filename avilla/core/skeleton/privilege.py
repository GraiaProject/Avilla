from __future__ import annotations

from datetime import timedelta

from avilla.core.abstract.trait import Fn, TBounded, Trait
from avilla.core.utilles.selector import Selector


class PrivilegeTrait(Trait[TBounded]):
    @Fn.bound
    async def upgrade(self, dest: str | None = None) -> None:
        ...

    @Fn.bound
    async def downgrade(self, dest: str | None = None) -> None:
        ...


class MuteTrait(Trait[TBounded]):
    @Fn.bound
    async def mute(self, duration: timedelta) -> None:
        ...

    @Fn.bound
    async def unmute(self) -> None:
        ...


class MuteAllTrait(Trait[TBounded]):
    @Fn.bound
    async def mute_all(self) -> None:
        ...

    @Fn.bound
    async def unmute_all(self) -> None:
        ...

    # Fetch => rs.pull(MuteInfo, target=...)


class BanTrait(Trait[TBounded]):
    @Fn.bound
    async def ban(self, duration: timedelta | None = None) -> None:
        ...

    @Fn.bound
    async def unban(self) -> None:
        ...
