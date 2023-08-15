from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.ryanvk import Capability, TargetFn, TargetMetadataUnitedFn


class SummaryCapability(Capability):
    @TargetMetadataUnitedFn
    async def set_name(self, name: str) -> None:
        ...

    @TargetMetadataUnitedFn
    async def unset_name(self) -> None:
        ...

    @TargetMetadataUnitedFn
    async def set_description(self, description: str) -> None:
        ...

    @TargetMetadataUnitedFn
    async def unset_description(self) -> None:
        ...


class NickCapability(Capability):
    @TargetMetadataUnitedFn
    async def set_name(self, name: str) -> None:
        ...

    @TargetFn
    async def set_nickname(self, nickname: str) -> None:
        ...

    @TargetFn
    async def unset_nickname(self) -> None:
        ...

    @TargetFn
    async def set_badge(self, badge: str) -> None:
        ...

    @TargetFn
    async def unset_badge(self) -> None:
        ...


class AvatarFetch(Capability):
    @TargetFn
    def get_avatar(self) -> Resource[bytes]:
        ...
