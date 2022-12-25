from __future__ import annotations

from datetime import timedelta

from avilla.core.trait import Fn, Trait


class PrivilegeTrait(Trait):
    @Fn.bound_entity
    async def upgrade(self, dest: str | None = None) -> None:
        ...

    @Fn.bound_entity
    async def downgrade(self, dest: str | None = None) -> None:
        ...


class MuteTrait(Trait):
    @Fn.bound_entity
    async def mute(self, duration: timedelta) -> None:
        ...

    @Fn.bound_entity
    async def unmute(self) -> None:
        ...


class MuteAllTrait(Trait):
    @Fn.bound_entity
    async def mute_all(self) -> None:
        ...

    @Fn.bound_entity
    async def unmute_all(self) -> None:
        ...

    # Fetch => rs.pull(MuteInfo, target=...)


class BanTrait(Trait):
    @Fn.bound_entity
    async def ban(self, duration: timedelta | None = None) -> None:
        ...

    @Fn.bound_entity
    async def unban(self) -> None:
        ...
