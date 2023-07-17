from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ChainMap,
    Protocol,
    TypeVar,
    overload,
)

from typing_extensions import Concatenate, ParamSpec

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.ryanvk.descriptor.target import TargetFn
from avilla.core.selector import Selectable
from avilla.core.utilles import identity

if TYPE_CHECKING:
    from avilla.core.metadata import Metadata, MetadataRoute
    from avilla.core.ryanvk.capability import Capability
    from avilla.core.selector import Selector


P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", covariant=True)
R1 = TypeVar("R1", covariant=True)
R2 = TypeVar("R2", covariant=True)
C = TypeVar("C", bound="Capability")


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


@dataclass
class UnitedFnImplement:
    capability: type[Capability]
    name: str
    metadata: type[Metadata] | MetadataRoute | None = None


class TargetMetadataUnitedFn(TargetFn[Concatenate["type[Metadata] | MetadataRoute | None", P], R]):
    def __init__(self, template: Callable[Concatenate[C, P], Awaitable[R]]) -> None:
        self.template = template

    def get_artifact_signature(
        self,
        collection: ChainMap[Any, Any],
        target: Selectable,
        route: type[Metadata] | MetadataRoute | None,
    ) -> Any:
        return UnitedFnImplement(self.capability, self.name, route)

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__
