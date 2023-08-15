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
    post_applying: bool = False

    def __init__(self):
        super().__init__()

    def __post_collected__(self, cls: type[BasePerform]):
        self.cls = cls
        if self.post_applying:
            self.apply_soon()

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

    def apply_soon(self, map: dict[Any, Any] | None = None):
        map = map or processing_artifact_heap.get()

        @self.on_collected
        def applier(cls: type[BasePerform]):
            # merge targetfn tree
            artifacts = cls.__collector__.artifacts
            if "lookup_collections" in artifacts:
                lookup_origin = artifacts.pop("lookup_collections")
                lookup_master = map.setdefault("lookup_collections", {})
                _merge_lookup_collection(lookup_master, lookup_origin)

            map.update(cls.__collector__.artifacts)
