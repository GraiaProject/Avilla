from __future__ import annotations

from datetime import timedelta

from avilla.core.traitof import Fn, Trait
from avilla.core.utilles.selector import Selector


class Privilege(Trait):
    @Fn
    async def upgrade(self, target: Selector, dest: str | None = None) -> None:
        ...

    @Fn
    async def downgrade(self, target: Selector, dest: str | None = None) -> None:
        ...


class Mute(Trait):
    @Fn
    async def mute(self, target: Selector, duration: timedelta) -> None:
        ...

    @Fn
    async def unmute(self, target: Selector) -> None:
        ...

    @Fn
    async def mute_all(self, target: Selector) -> None:
        ...
    
    @Fn
    async def unmute_all(self, target: Selector) -> None:
        ...

    # Fetch => rs.pull(MuteInfo, target=...)


class Ban(Trait):
    @Fn
    async def ban(self, target: Selector, duration: timedelta | None = None) -> None:
        ...

    @Fn
    async def unban(self, target: Selector) -> None:
        ...
