from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, ChainMap, Generic, TypeVar, Union, cast, overload

from typing_extensions import ParamSpec, TypeAlias, Unpack

from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.ryanvk.descriptor.target import LookupBranch, TargetArtifactStore, TargetFn
from avilla.core.selector import FollowsPredicater, Selectable, Selector
from graia.ryanvk import BaseCollector

P = ParamSpec("P")
R = TypeVar("R", covariant=True)
M = TypeVar("M", bound="Metadata")
M1 = TypeVar("M1", bound="Metadata")

Route: TypeAlias = "Union[type[M], MetadataRoute[Unpack[tuple[Metadata, ...]], M]]"


@dataclass(unsafe_hash=True)
class PullImplement(Generic[M]):
    route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]


class PullFn(
    TargetFn[[Route[M]], Awaitable[M]] if TYPE_CHECKING else TargetFn,
):
    def __init__(self):
        ...

    @overload
    def collect(
        self: PullFn[M],
        collector: BaseCollector,
        pattern: str,
        route: type[M],
        **kwargs: FollowsPredicater,
    ) -> Callable[[Callable[[Any, Selector], Awaitable[M]]], Callable[[Any, Selector], Awaitable[M]]]:
        ...

    @overload
    def collect(
        self: PullFn[M],
        collector: BaseCollector,
        pattern: str,
        route: MetadataRoute[Unpack[tuple[Any, ...]], M],
        **kwargs: FollowsPredicater,
    ) -> Callable[[Callable[[Any, Selector], Awaitable[M]]], Callable[[Any, Selector], Awaitable[M]],]:
        ...

    def collect(
        self: PullFn[M],
        collector: BaseCollector,
        pattern: str,
        route: ...,
        **kwargs: FollowsPredicater,
    ) -> ...:
        def receive(entity: Callable[[Any, Selector], Awaitable[M]]):
            branch = self.get_collect_layout(collector, pattern, **kwargs)
            branch = cast("LookupBranch[Callable[[Any, Selector], Awaitable[M]]]", branch)
            signature = PullImplement(route)
            artifact = TargetArtifactStore(collector, entity)
            branch.artifacts[signature] = artifact
            return entity

        return receive

    def get_artifact_signature(
        self: PullFn[M],
        collection: ChainMap[Any, Any],
        target: Selectable,
        route: Route[M],
    ) -> Any:
        return PullImplement(route)

    def get_outbound_callable(self, instance: Any, entity: Callable[[Any, Selector], Awaitable[M]]):
        def wrapper(target: Selector, route: ...):
            return entity(instance, target)

        return wrapper

    def __repr__(self) -> str:
        return "<Fn#pull>"
