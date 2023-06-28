from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Mapping,
    MutableMapping,
    Protocol,
    TypedDict,
    TypeVar,
)

from typing_extensions import Concatenate, ParamSpec, TypeAlias

from ...selector import _parse_follows
from ...utilles import identity
from ..common.fn import FnImplement
from .base import Fn
from .utilles import doubledself

if TYPE_CHECKING:
    from ...context import Context
    from ...selector import FollowsPredicater, Selectable, Selector, _FollowItem
    from ..collector import AvillaPerformTemplate, Collector
    from ..common.capability import Capability


P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", covariant=True)
R1 = TypeVar("R1", covariant=True)
C = TypeVar("C", bound="Capability")
T = TypeVar("T")
X = TypeVar("X")


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
    Fn[Concatenate[Selectable, P], R],
):
    def __init__(self, template: Callable[Concatenate[C, P], R]) -> None:
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

    def get_collect_signature(self, entity: Callable[Concatenate[AvillaPerformTemplate, "Selector", P], R]) -> Any:
        return FnImplement(self.capability, self.name)

    @doubledself
    def get_execute_layout(
        self, self1: Fn._InferProtocol[R1], runner: Context, target: Selectable, *args: P.args, **kwargs: P.kwargs
    ) -> Mapping[R1, tuple[Collector, Callable[Concatenate[AvillaPerformTemplate, P], R]]]:
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
