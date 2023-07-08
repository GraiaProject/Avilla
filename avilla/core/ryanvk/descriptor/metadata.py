from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Protocol, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec

from ..._vendor.dataclasses import dataclass
from ...utilles import identity
from .target import TargetFn, VnCollector, VnRunner

if TYPE_CHECKING:
    from ...metadata import Metadata, MetadataRoute
    from .base import Fn
    from ...selector import Selectable, Selector
    from ..capability import Capability


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


class TargetMetadataUnitedFn(
    TargetFn[Concatenate["type[Metadata] | MetadataRoute | None", P], R, VnCollector, VnRunner]
):
    def __init__(self, template: Callable[Concatenate[C, P], Awaitable[R]]) -> None:
        self.template = template

    @overload
    def execute(
        self: Fn[UnitedFnPerformBranch[P1, R1, Any], VnCollector, VnRunner],
        runner: VnRunner,
        target: Selectable,
        metadata: None = None,
        *args: P1.args,
        **kwargs: P1.kwargs,
    ) -> R1:
        ...

    @overload
    def execute(
        self: Fn[UnitedFnPerformBranch[P1, Any, R2], VnCollector, VnRunner],
        runner: VnRunner,
        target: Selectable,
        metadata: type[Metadata] | MetadataRoute,
        *args: P1.args,
        **kwargs: P1.kwargs,
    ) -> R2:
        ...

    def execute(
        self,
        runner: VnRunner,
        target: Selectable,
        metadata: type[Metadata] | MetadataRoute | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        return super().execute(runner, target, metadata, *args, **kwargs)

    def get_artifact_record(
        self: TargetMetadataUnitedFn[P, R, VnCollector, VnRunner],
        runner: VnRunner,
        target: Selectable,
        metadata: type[Metadata] | MetadataRoute | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[VnCollector, Callable[Concatenate[Any, Selector, type[Metadata] | MetadataRoute | None, P], R]]:
        sign = UnitedFnImplement(self.capability, self.name, metadata)
        select = target.to_selector()
        for branch in self._iter_branches(runner.artifacts.maps, select):
            if sign in branch.artifacts:
                artifact = branch.artifacts[sign]
                return artifact.collector, artifact.entity
        raise NotImplementedError(f"no {repr(self)} implements for {select}.")

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__
