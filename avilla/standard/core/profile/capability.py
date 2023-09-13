from __future__ import annotations

from avilla.core.metadata import Route
from avilla.core.resource import Resource
from avilla.core.ryanvk import Capability, Fn, MetadataOverload, TargetOverload
from avilla.core.selector import Selector


class SummaryCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"], MetadataOverload(): ["route"]})
    async def set_name(self, target: Selector, route: Route, name: str) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"], MetadataOverload(): ["route"]})
    async def unset_name(self, target: Selector, route: Route) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"], MetadataOverload(): ["route"]})
    async def set_description(self, target: Selector, route: Route, description: str) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"], MetadataOverload(): ["route"]})
    async def unset_description(self, target: Selector, route: Route) -> None:
        ...


class NickCapability(Capability):
    @Fn.complex({TargetOverload(): ["target"], MetadataOverload(): ["route"]})
    async def set_name(self, target: Selector, route: Route, name: str) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def set_nickname(self, target: Selector, nickname: str) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def unset_nickname(self, target: Selector) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def set_badge(self, target: Selector, badge: str) -> None:
        ...

    @Fn.complex({TargetOverload(): ["target"]})
    async def unset_badge(self, target: Selector) -> None:
        ...


class AvatarFetch(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    def get_avatar(self, target: Selector) -> Resource[bytes]:
        ...
