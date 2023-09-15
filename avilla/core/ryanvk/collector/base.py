from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar, overload

from avilla.core.ryanvk.descriptor.fetch import Fetch
from avilla.core.ryanvk.util import _merge_lookup_collection
from graia.ryanvk import BaseCollector, BasePerform
from graia.ryanvk._runtime import processing_artifact_heap

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from avilla.core.metadata import Metadata, MetadataRoute
    from avilla.core.selector import FollowsPredicater, Selector

T = TypeVar("T")
T1 = TypeVar("T1")

M = TypeVar("M", bound="Metadata")


class AvillaBaseCollector(BaseCollector):
    def __init__(self):
        super().__init__()

    @overload
    def pull(
        self, target: str, route: type[M], **patterns: FollowsPredicater
    ) -> Callable[[Callable[[Any, Selector], Awaitable[M]]], Callable[[Any, Selector], Awaitable[M]]]:
        ...

    @overload
    def pull(
        self, target: str, route: MetadataRoute[Unpack[tuple[Any, ...]], M], **patterns: FollowsPredicater
    ) -> Callable[[Callable[[Any, Selector], Awaitable[M]]], Callable[[Any, Selector], Awaitable[M]]]:
        ...

    def pull(self, target: str, route: ..., **patterns: FollowsPredicater) -> ...:
        from avilla.core.builtins.capability import CoreCapability

        return self.entity(CoreCapability.pull, target, route, **patterns)

    def fetch(self, resource_type: type[T]):  # type: ignore[reportInvalidTypeVarUse]
        return self.entity(Fetch, resource_type)
