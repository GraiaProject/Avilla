from __future__ import annotations

from avilla.core.ryanvk.descriptor.metadata import TargetFn
from avilla.core.selector import Selector
from graia.ryanvk.capability import Capability


class RoleCreate(Capability):
    @TargetFn
    async def create(self, name: str, hoist: bool | None = None, color: int | None = None) -> Selector:
        ...


class RoleDelete(Capability):
    @TargetFn
    async def delete(self) -> None:
        ...


class RoleEdit(Capability):
    @TargetFn
    async def edit(self, name: str | None = None, hoist: bool | None = None, color: int | None = None) -> None:
        ...


class RoleMemberCapability(Capability):
    @TargetFn
    async def add(self, member: Selector) -> None:
        ...

    @TargetFn
    async def remove(self, member: Selector) -> None:
        ...
