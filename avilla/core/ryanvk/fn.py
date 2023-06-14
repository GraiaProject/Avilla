from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    MutableMapping,
    TypedDict,
    TypeVar,
    cast,
)

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
from .common.fn import BaseFn

if TYPE_CHECKING:
    from avilla.core.ryanvk.collector import _AvillaPerformTemplate

    from ..context import Context
    from ..metadata import Metadata, MetadataRoute
    from .collector import Collector
    from .common.capability import Capability
    from .common.protocol import Ring3


P = ParamSpec("P")
R = TypeVar("R", covariant=True)
N = TypeVar("N", bound="Ring3")
T = TypeVar("T")

class Fn(BaseFn[P, R]):
    def __init__(self, template: Callable[Concatenate[Capability, P], R]) -> None:
        self.template = template  # type: ignore

    def collect(self, collector: Collector):
        def receive(entity: Callable[Concatenate[_AvillaPerformTemplate, P], R]):
            collector.artifacts[self.signature] = (collector, entity)
            return entity

        return receive

    def execute(self, runner: Context, *args: P.args, **kwargs: P.kwargs) -> R:
        collector, entity = cast(
            "tuple[Collector, Callable[Concatenate[_AvillaPerformTemplate, P], R]]", runner.artifacts[self.signature]
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


class TargetEntity(Generic[P, T]):
    if TYPE_CHECKING:

        @property
        def signature(self):
            ...

    def collect(
        self, collector: Collector, pattern: tuple[str, dict[str, FollowsPredicater]], *args: P.args, **kwargs: P.kwargs
    ):
        def receive(entity: T):
            self.__collect_extended__(*args, **kwargs)
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

            branch["artifacts"][self.signature] = {"collector": collector, "entity": entity, "pattern": items}
            self.__post_collected__(branch["artifacts"][self.signature])
            return entity

        return receive

    def __post_collected__(self, artifact: TargetArtifactStore[T]):
        ...

    def __collect_extended__(self, *args: P.args, **kwargs: P.kwargs):
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

    def get_artifacts(self, artifacts: dict[Any, Any]) -> TargetArtifactStore[T]:
        return artifacts[self.signature]


# the Inbound & Outbound!
# Inbound: 用户看到的 Capability 侧
# Outbound: Perform 侧


class TargetFn(
    TargetEntity[[], Callable[Concatenate["_AvillaPerformTemplate", "Selector", P], Awaitable[R]]],
    Fn[Concatenate["Selector", P], Awaitable[R]],
):
    def __init__(self, template: Callable[Concatenate[Capability, "Selector", P], R]) -> None:
        self.template = template  # type: ignore

    def execute(self, runner: Context, target: Selectable, *args: P.args, **kwargs: P.kwargs):
        for branch in self.iter_branches(runner.artifacts.maps, target.to_selector()):
            artifact = self.get_artifacts(branch["artifacts"])
            if artifact is not None:
                collector = artifact["collector"]
                entity = artifact["entity"]
                instance = collector.cls(runner)
                return entity(instance, target.to_selector(), *args, **kwargs)
        raise NotImplementedError(f"no {repr(self)} implements for {target.to_selector()}.")

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__


M = TypeVar("M", bound="Metadata")


@dataclass
class PullImplements(Generic[M]):
    route: type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]


class PullFn(
    TargetEntity[
        ["type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]"],
        Callable[["_AvillaPerformTemplate", "Selector"], Awaitable[M]],
    ],
    Fn[["Selector", "type[M] | MetadataRoute[Unpack[tuple[Metadata, ...]], M]"], Awaitable[M]],
):
    @property
    def signature(self):
        return PullImplements(self._route)

    def execute(self, runner: Context, target: Selectable):
        for branch in self.iter_branches(runner.artifacts.maps, target.to_selector()):
            artifact = self.get_artifacts(branch["artifacts"])
            if artifact is not None:
                collector = artifact["collector"]
                entity = artifact["entity"]
                instance = collector.cls(runner)
                return entity(instance, target.to_selector())
        raise NotImplementedError(f"no {repr(self)} implements for {target.to_selector()}.")

    def __repr__(self) -> str:
        return "<Fn#pull>"

    def __collect_extended__(self, route):
        self._route = route

    def __post_collected__(self, artifact: TargetArtifactStore[Callable[[_AvillaPerformTemplate, Selector], M]]):
        del self._route


Re = TypeVar("Re", bound='Resource')

class FetchFn(
    TargetEntity[
        ['type[Re]'],
        Callable[["_AvillaPerformTemplate", "Selector", "Re"], Any],
    ],
    Fn[["Selector", "Resource[T]"], Awaitable[T]],
):
    @property
    def signature(self):
        return PullImplements(self._route)

    def execute(self, runner: Context, target: Selectable, resource: Re):
        for branch in self.iter_branches(runner.artifacts.maps, target.to_selector()):
            artifact = self.get_artifacts(branch["artifacts"])
            if artifact is not None:
                collector = artifact["collector"]
                entity = artifact["entity"]
                instance = collector.cls(runner)
                return entity(instance, target.to_selector(), resource)
        raise NotImplementedError(f"no {repr(self)} implements for {target.to_selector()}.")

    def __repr__(self) -> str:
        return "<Fn#pull internal!>"

    def __collect_extended__(self, route):
        self._route = route

    def __post_collected__(self, artifact: TargetArtifactStore[Callable[[_AvillaPerformTemplate, Selector], M]]):
        del self._route

