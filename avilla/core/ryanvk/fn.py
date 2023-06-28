from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Generic,
    Mapping,
    MutableMapping,
    Protocol,
    TypedDict,
    overload,
)
from typing import NoReturn as Never

from typing_extensions import Concatenate, ParamSpec, Self, TypeAlias, TypeVar, Unpack

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
    from avilla.core.resource import Resource

    from ..context import Context
    from ..metadata import Metadata, MetadataRoute
    from .collector import AvillaPerformTemplate, Collector
    from .common.capability import Capability
    from .common.protocol import Ring3


P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", covariant=True)
R1 = TypeVar("R1", covariant=True)
N = TypeVar("N", bound="Ring3")
C = TypeVar("C", bound="Capability")
H = TypeVar("H", bound="AvillaPerformTemplate")
T = TypeVar("T")
X = TypeVar("X")

A = TypeVar("A", infer_variance=True)


class doubledself(Generic[T, P, R]):
    """和普通的方法差不多, 唯一的差别就是 self 会传两个, (self0, self1, ...), 用于制服 pyright.
    有一个问题, 就是强行 apply 上原方法会寄. 我需要一种能自动取两个 var 并集的 type operator 方法,
    或者我就只能 type: ignore
    """

    def __init__(self, fn: Callable[Concatenate[T, T, P], R]):
        self.fn = fn

    @overload
    def __get__(self, instance: None, owner: type[T]) -> Self:
        ...

    @overload
    def __get__(self, instance: T, owner: type[T]) -> Callable[P, R]:
        ...

    def __get__(self, instance: T | None, owner: type[T]):
        if instance is None:
            return self

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return self.fn(instance, instance, *args, **kwargs)

        return wrapper


class Fn(BaseFn["Collector", P, R]):
    def __init__(self, template: Callable[Concatenate[C, P], R]) -> None:
        self.template = template  # type: ignore

    def collect(self, collector: Collector):
        def receive(entity: Callable[Concatenate[H, P], R]):
            collector.artifacts[FnImplement(self.capability, self.name)] = (collector, entity)
            return entity

        return receive

    def get_collect_signature(self):
        return FnImplement(self.capability, self.name)

    def get_execute_signature(self, runner: Context, *args: P.args, **kwargs: P.kwargs) -> Any:
        return FnImplement(self.capability, self.name)

    class _InferProtocol(Protocol[R1]):
        def get_execute_signature(self, runner: Context, *args, **kwargs) -> R1:
            ...

    def get_execute_layout(
        self: _InferProtocol[R1], runner: Context, *args: P.args, **kwargs: P.kwargs
    ) -> Mapping[R1, tuple[Collector, Callable[Concatenate[AvillaPerformTemplate, P], R]]]:
        return runner.artifacts

    def execute(self, runner: Context, *args: P.args, **kwargs: P.kwargs) -> R:
        collector, entity = self.get_execute_layout(runner, *args, **kwargs)[
            self.get_execute_signature(runner, *args, **kwargs)
        ]
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
    def get_collect_signature(self, entity: T, *args: P.args, **kwargs: P.kwargs) -> Any:
        ...

    def __post_collected__(self, artifact: TargetArtifactStore[T]):
        ...


# the Inbound & Outbound!
# Inbound: 用户看到的 Capability 侧
# Outbound: Perform 侧


class TargetFn(
    Fn[Concatenate[Selectable, P], Awaitable[R]],
):
    def __init__(self, template: Callable[Concatenate[C, P], Awaitable[R]]) -> None:
        self.template = template  # type: ignore

    def collect(
        self: TargetEntityProtocol[P1, T],  # type: ignore
        collector: Collector,
        pattern: tuple[str, dict[str, FollowsPredicater]],
        *args: P1.args,
        **kwargs: P1.kwargs,
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

            signature = self.get_collect_signature(entity, *args, **kwargs)
            artifact: TargetArtifactStore = {"collector": collector, "entity": entity, "pattern": items}
            branch["artifacts"][signature] = artifact
            self.__post_collected__(artifact)
            return entity

        return receive

    def __post_collected__(self, artifact):
        ...

    @staticmethod
    def _iter_branches(collections: list[MutableMapping[Any, Any]], target: Selector):
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

    def get_collect_signature(
        self, entity: Callable[Concatenate[AvillaPerformTemplate, "Selector", P], Awaitable[R]]
    ) -> Any:
        return FnImplement(self.capability, self.name)

    @doubledself
    def get_execute_layout(
        self, self1: Fn._InferProtocol[R1], runner: Context, target: Selectable, *args: P.args, **kwargs: P.kwargs
    ) -> Mapping[R1, tuple[Collector, Callable[Concatenate[AvillaPerformTemplate, P], Awaitable[R]]]]:
        sign = self.get_execute_signature(runner, target, *args, **kwargs)
        for branch in self._iter_branches(runner.artifacts.maps, target.to_selector()):
            artifacts = branch["artifacts"]
            if sign in artifacts:
                return artifacts
        raise NotImplementedError(f"no {repr(self)} implements for {target.to_selector()}.")

    def get_execute_signature(self, runner: Context, _, *args: P.args, **kwargs: P.kwargs) -> Any:
        return FnImplement(self.capability, self.name)

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


class TargetMetadataUnitedFn(TargetFn[Concatenate["type[Metadata] | MetadataRoute | None", P], R]):
    def __init__(self, template: Callable[Concatenate[C, P], Awaitable[R]]) -> None:
        self.template = template  # type: ignore

    def __post_received__(self, entity: UnitedFnPerformBranch[P, R1, R2]):  # type: ignore
        ...

    @overload
    async def execute(
        self: PostReceivedCallback[R1, Any],
        runner: Context,
        target: Selectable,
        metadata: None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R1:
        ...

    @overload
    async def execute(
        self: PostReceivedCallback[Any, R2],
        runner: Context,
        target: Selectable,
        metadata: type[Metadata] | MetadataRoute,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R2:
        ...

    async def execute(
        self,
        runner: Context,
        target: Selectable,
        metadata: type[Metadata] | MetadataRoute | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        return await super().execute(runner, target, metadata, *args, **kwargs)

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


M = TypeVar("M", bound="Metadata")


@dataclass(unsafe_hash=True)
class PullImplement(Generic[M]):
    route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]


class PullFn(
    TargetFn[["type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]"], Awaitable[M]],
):
    def __init__(self):
        ...

    def get_collect_signature(
        self,
        entity: Callable[[AvillaPerformTemplate, "Selector"], Awaitable[M]],
        route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M],
    ) -> Any:
        return PullImplement(route)

    def get_execute_signature(self, route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]):
        return PullImplement(route)

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

    def get_execute_signature(self, runner: Context, resource_type: type[Resource]) -> Any:
        return FetchImplement(resource_type)

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
