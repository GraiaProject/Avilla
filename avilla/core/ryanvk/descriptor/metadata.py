from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ChainMap,
    Protocol,
    TypeVar,
    overload,
)

from typing_extensions import Concatenate, ParamSpec

from avilla.core.ryanvk.descriptor.target import TargetArtifactStore, TargetFn
from avilla.core.selector import FollowsPredicater, Selectable
from avilla.core.utilles import identity
from graia.ryanvk import BaseCollector, BasePerform, Capability

if TYPE_CHECKING:
    from avilla.core.metadata import Metadata, MetadataRoute
    from avilla.core.selector import Selector


P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", covariant=True)
R1 = TypeVar("R1", covariant=True)
R2 = TypeVar("R2", covariant=True)
HQ = TypeVar("HQ", bound="BasePerform", contravariant=True)


class UnitedFnPerformBranch(Protocol[P, R1, R2]):
    @overload
    def __call__(self, target: Selector, metadata: None = None, *args: P.args, **kwargs: P.kwargs) -> R1:
        ...

    @overload
    def __call__(
        self, target: Selector, metadata: type[Metadata] | MetadataRoute, *args: P.args, **kwargs: P.kwargs
    ) -> R2:
        ...

    def __call__(
        self, target: ..., metadata: type[Metadata] | MetadataRoute | None = None, *args: P.args, **kwargs: P.kwargs
    ) -> R1 | R2:
        ...


@dataclass(unsafe_hash=True)
class UnitedFnImplement:
    capability: type[BasePerform | Capability]
    name: str
    metadata: type[Metadata] | MetadataRoute | None = None


class TargetMetadataUnitedFn(TargetFn[Concatenate["type[Metadata] | MetadataRoute", P], R]):
    def __init__(self, template: Callable[Concatenate[Any, P], R]) -> None:
        self.template = template

    def get_collect_signature(
        self,
        collector: BaseCollector,
        pattern: str,
        route: type[Metadata] | MetadataRoute,
        **kwargs: FollowsPredicater,
    ):
        return UnitedFnImplement(self.owner, self.name, route)

    def collect(
        self,
        collector: BaseCollector,
        pattern: str,
        route: type[Metadata] | MetadataRoute,
        **kwargs: FollowsPredicater,
    ):
        def receive(entity: Callable[Concatenate[HQ, Selector, type[Metadata] | MetadataRoute, P], R]):
            branch = self.get_collect_layout(collector, pattern, **kwargs)
            signature = self.get_collect_signature(collector, pattern, route, **kwargs)
            artifact = TargetArtifactStore(collector, entity)
            branch.artifacts[signature] = artifact
            return entity

        return receive

    def get_artifact_signature(
        self,
        collection: ChainMap[Any, Any],
        target: Selectable,
        route: type[Metadata] | MetadataRoute | None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        return UnitedFnImplement(self.owner, self.name, route)

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.owner)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__
