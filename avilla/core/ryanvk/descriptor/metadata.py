from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Protocol, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec

from ..._vendor.dataclasses import dataclass
from ...utilles import identity
from .target import TargetEntityProtocol, TargetFn
from .utilles import doubledself

if TYPE_CHECKING:
    from ...context import Context
    from ...metadata import Metadata, MetadataRoute
    from ...selector import Selectable, Selector
    from ..common.capability import Capability


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


class PostReceivedCallback(Protocol[R1, R2]):  # type: ignore[reportInvalidGenericUse]
    def __post_received__(self, entity: UnitedFnPerformBranch[Any, R1, R2]):
        ...


class TargetMetadataUnitedFn(TargetFn[Concatenate["type[Metadata] | MetadataRoute | None", P], R]):
    def __init__(self, template: Callable[Concatenate[C, P], Awaitable[R]]) -> None:
        self.template = template  # type: ignore

    def __post_received__(self, entity: UnitedFnPerformBranch[P, R1, R2]):  # type: ignore
        ...

    @overload
    def execute(
        self: PostReceivedCallback[R1, Any],
        runner: Context,
        target: Selectable,
        metadata: None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R1:
        ...

    @overload
    def execute(
        self: PostReceivedCallback[Any, R2],
        runner: Context,
        target: Selectable,
        metadata: type[Metadata] | MetadataRoute,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R2:
        ...

    def execute(
        self,
        runner: Context,
        target: Selectable,
        metadata: type[Metadata] | MetadataRoute | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        return super().execute(runner, target, metadata, *args, **kwargs)

    @doubledself  # type: ignore
    def get_execute_signature(
        self,
        self1: TargetEntityProtocol[P1, Any],
        runner: Context,
        _,
        metadata: type[Metadata] | MetadataRoute | None = None,
        *args: P1.args,
        **kwargs: P1.kwargs,
    ) -> Any:
        return UnitedFnImplement(self.capability, self.name, metadata)

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__
