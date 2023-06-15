from __future__ import annotations
from typing import TYPE_CHECKING

from avilla.core.ryanvk import TargetMetadataUnitedFn, Capability, TargetFn

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
    async def set_name(self, selector, metadata, name: str) -> None:
        ...

    @TargetFn
    async def set_nickname(self, selector, nickname: str) -> None:
        ...

    @TargetFn
    async def unset_nickname(self, selector) -> None:
        ...

    @TargetFn
    async def set_badge(self, selector, badge: str) -> None:
        ...

    @TargetFn
    async def unset_badge(self) -> None:
        ...
