from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ChainMap,
    Generic,
    TypeVar,
    Union,
)

from typing_extensions import ParamSpec, TypeAlias, Unpack

from avilla.core.selector import FollowsPredicater, Selectable, Selector

from ..._vendor.dataclasses import dataclass
from ...metadata import Metadata, MetadataRoute
from .target import TargetArtifactStore, TargetFn

if TYPE_CHECKING:
    from .base import BaseCollector
    from .target import HQ

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

    def into(self, route: type[M1] | MetadataRoute[Unpack[tuple[Metadata, ...]], M1]) -> PullFn[M1]:
        return self  # type: ignore[reportGeneral]

    def collect(
        self: PullFn[M],
        collector: BaseCollector,
        pattern: str,
        route: Route[M],
        **kwargs: FollowsPredicater,
    ):
        def receive(entity: Callable[[HQ, Selector, Route[M]], Awaitable[M]]):
            branch = self.get_collect_layout(collector, pattern, **kwargs)
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

    def __repr__(self) -> str:
        return "<Fn#pull>"
