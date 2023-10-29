from __future__ import annotations

from avilla.core.ryanvk import Fn, TargetOverload
from avilla.core.selector import Selector
from graia.ryanvk.capability import Capability


class RoleCreate(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def create(
        self, target: Selector, name: str, hoist: bool | None = None, color: int | None = None
    ) -> Selector:
        ...


class RoleDelete(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def delete(self, target: Selector) -> None:
        ...


class RoleEdit(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def edit(
        self, target: Selector, name: str | None = None, hoist: bool | None = None, color: int | None = None
    ) -> None:
        ...


class RoleMemberCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def add(self, target: Selector, member: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def remove(self, target: Selector, member: Selector) -> None:
        ...
