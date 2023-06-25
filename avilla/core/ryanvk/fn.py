from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Callable, Generic, MutableMapping
from typing import NoReturn as Never
from typing import Protocol, TypedDict, TypeVar, cast, overload

from typing_extensions import Concatenate, ParamSpec, TypeAlias, Unpack

from avilla.core.resource import Resource

from .._vendor.dataclasses import dataclass
from ..selector import (
    FollowsPredicater,
    Selectable,
    Selector,
    _FollowItem,
    _parse_follows,
)
from ..utilles import identity
from .common.fn import BaseFn, FnImplement

if TYPE_CHECKING:
    from ..context import Context
    from ..metadata import Metadata, MetadataRoute
    from .collector import AvillaPerformTemplate, Collector
    from .common.capability import Capability
    from .common.protocol import Ring3


P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", covariant=True)
N = TypeVar("N", bound="Ring3")
C = TypeVar("C", bound="Capability")
H = TypeVar("H", bound="AvillaPerformTemplate")
T = TypeVar("T")
X = TypeVar("X")


class Fn(BaseFn[P, R]):
    def __init__(self, template: Callable[Concatenate[C, P], R]) -> None:
        self.template = template  # type: ignore

    def collect(self, collector: Collector):
        def receive(entity: Callable[Concatenate[H, P], R]):
            collector.artifacts[self.signature_on_collect()] = (collector, entity)
            return entity

        return receive

    def execute(self, runner: Context, *args: P.args, **kwargs: P.kwargs) -> R:
        collector, entity = cast(
            "tuple[Collector, Callable[Concatenate[AvillaPerformTemplate, P], R]]",
            runner.artifacts[self.signature_on_collect()],
        )
        instance = collector.cls(runner)
        return entity(instance, *args, **kwargs)


class LookupBranchMetadata(TypedDict):
    override: bool


class LookupBranch(TypedDict):
    metadata: LookupBranchMetadata
    levels: LookupCollection
    artifacts: dict[Any, Any]


class TargetArtifactStore(TypedDict, Generic[T]):
    collector: Collector
    entity: T
    pattern: list[_FollowItem]


LookupBranches: TypeAlias = "dict[str | FollowsPredicater | None, LookupBranch]"
LookupCollection: TypeAlias = "dict[str, LookupBranches]"


class TargetEntityProtocol(Protocol[P, T]):
    def signature_on_collect(self, *args: P.args, **kwargs: P.kwargs) -> Any:
        ...

    def __post_collected__(self, artifact: TargetArtifactStore[T]):
        ...

    def __post_received__(self, entity: T):
        ...


class TargetEntity:
    def collect(
        self: TargetEntityProtocol[P, T],  # type: ignore
        collector: Collector,
        pattern: tuple[str, dict[str, FollowsPredicater]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        def receive(entity: T):
            target, predicaters = pattern
            items = _parse_follows(target, **predicaters)
            if not items:
                raise ValueError("invalid target pattern")
            collection: LookupCollection = collector.artifacts["lookup"]
            if TYPE_CHECKING:
                branch = {"metadata": {"override": True}, "levels": {}, "artifacts": {}}
            for i in items:
                if i.name not in collection:
                    collection[i.name] = {}
                branches = collection[i.name]

                if (i.literal or i.predicate) in branches:
                    branch = branches[i.literal or i.predicate]
                else:
                    branch: LookupBranch = {"metadata": {"override": True}, "levels": {}, "artifacts": {}}
                    branches[i.literal or i.predicate] = branch

                collection = branch["levels"]

            signature = self.signature_on_collect(*args, **kwargs)
            branch["artifacts"][signature] = {"collector": collector, "entity": entity, "pattern": items}
            self.__post_collected__(branch["artifacts"][signature])
            return entity

        return receive

    def __post_collected__(self, artifact):
        ...

    def __post_received__(self, entity):
        ...

    def iter_branches(self, collections: list[MutableMapping[Any, Any]], target: Selector):
        lookups: list[LookupCollection] = [i["lookup"] for i in collections]

        for i in lookups:
            # get branch
            collection = i
            branch = None
            for k, v in target.pattern.items():
                if k not in collection:
                    break
                branches = collection[k]
                if v in branches:
                    header = v
                else:
                    header = None
                    for header, branch in branches.items():
                        if not callable(header):
                            continue
                        if header(v):
                            break
                    else:
                        if None not in branches:
                            break
                        header = None

                branch = branches[header]
                collection = branch["levels"]
                if header is not None:
                    if branch["metadata"]["override"] and None in branches:
                        collection = {**branches[None]["levels"], **collection}
            if branch is None:
                continue

            yield branch

    def get_artifacts(
        self: TargetEntityProtocol[Any, T], artifacts: dict[Any, Any], signature: Any
    ) -> TargetArtifactStore[T]:
        return artifacts[signature]


# the Inbound & Outbound!
# Inbound: 用户看到的 Capability 侧
# Outbound: Perform 侧


class TargetFn(
    TargetEntity,
    Fn[P, Awaitable[R]],
):
    def __post_received__(self, entity: Callable[Concatenate[AvillaPerformTemplate, "Selector", P], Awaitable[R]]):
        ...

    def execute(self, runner: Context, target: Selectable, *args: P.args, **kwargs: P.kwargs):
        for branch in self.iter_branches(runner.artifacts.maps, target.to_selector()):
            artifact = self.get_artifacts(branch["artifacts"], FnImplement(self.capability, self.name))
            if artifact is not None:
                collector = artifact["collector"]
                entity = artifact["entity"]
                instance = collector.cls(runner)
                return entity(instance, target.to_selector(), *args, **kwargs)  # type: ignore
        raise NotImplementedError(f"no {repr(self)} implements for {target.to_selector()}.")

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__


R1 = TypeVar("R1", covariant=True)
R2 = TypeVar("R2", covariant=True)


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


class TargetMetadataUnitedFn(
    TargetEntity,
    Fn[P, Awaitable[Any]],
):
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
    ):
        for branch in self.iter_branches(runner.artifacts.maps, target.to_selector()):
            artifact = self.get_artifacts(branch["artifacts"], UnitedFnImplement(self.capability, self.name, metadata))
            if artifact is not None:
                collector = artifact["collector"]
                entity = artifact["entity"]
                instance = collector.cls(runner)
                return entity(instance, target.to_selector(), *args, **kwargs)  # type: ignore
        raise NotImplementedError(f"no {repr(self)} implements for {target.to_selector()}.")

    def signature_on_collect(self, metadata: type[Metadata] | MetadataRoute | None = None):
        return UnitedFnImplement(self.capability, self.name, metadata)

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__


M = TypeVar("M", bound="Metadata")


@dataclass(unsafe_hash=True)
class PullImplement(Generic[M]):
    route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]


class PullFn(
    TargetEntity,
    Fn[["Selector", "type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]"], Awaitable[M]],
):
    def __init__(self):
        ...

    def __post_received__(self, entity: Callable[[AvillaPerformTemplate, "Selector"], Awaitable[M]]):
        ...

    def signature_on_collect(self, route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]):
        return PullImplement(route)

    def execute(
        self, runner: Context, target: Selectable, route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]
    ):
        for branch in self.iter_branches(runner.artifacts.maps, target.to_selector()):
            artifact = self.get_artifacts(branch["artifacts"], PullImplement(route))
            if artifact is not None:
                collector = artifact["collector"]
                entity = artifact["entity"]
                instance = collector.cls(runner)
                return entity(instance, target.to_selector())  # type: ignore
        raise NotImplementedError(f"no {repr(self)} implements for {target.to_selector()}.")

    def __repr__(self) -> str:
        return "<Fn#pull>"


Re = TypeVar("Re", bound="Resource")


@dataclass(unsafe_hash=True)
class FetchImplement:
    resource: type[Resource]


class FetchFn(
    Fn[["type[Resource[T]]"], Awaitable[T]],
):
    def __init__(self):
        ...

    def into(self, resource_type: type[Resource[X]]) -> FetchFn[X]:
        return self  # type: ignore[reportGeneralTypeIssues]

    def collect(self, collector: Collector, resource_type: type[Resource[T]]):
        def receive(entity: Callable[[H, Never], Awaitable[T]]):  # to accept all resource type
            collector.artifacts[FetchImplement(resource_type)] = (collector, entity)
            return entity

        return receive

    def execute(self, runner: Context, resource: Resource[T]) -> Awaitable[T]:
        collector, entity = cast(
            "tuple[Collector, Callable[[Any, Resource[T]], Awaitable[T]]]",
            runner.artifacts[FetchImplement(type(resource))],
        )
        instance = collector.cls(runner)
        return entity(instance, resource)

    def __repr__(self) -> str:
        return "<Fn#pull internal!>"


@dataclass
class QueryRecord:
    """仅用作计算路径, 不参与实际运算, 也因此, 该元素仅存在于全局 Artifacts['query'] 中."""

    previous: str | None
    into: str


class QueryHandlerPerform(Protocol):
    def __call__(
        self, _p0: Never, predicate: Callable[[str, str], bool] | str, previous: Selector | None = None
    ) -> AsyncGenerator[Selector, None]:
        ...


class QuerySchema:
    def collect(self, collector: Collector, target: str, previous: str | None = None):
        def receive(entity: QueryHandlerPerform):
            collector.artifacts[QueryRecord(previous, target)] = (collector, entity)
            return entity

        return receive
