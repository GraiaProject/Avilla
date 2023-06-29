from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Generic,
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

if TYPE_CHECKING:
    from ...context import Context
    from ...selector import FollowsPredicater, Selectable, Selector, _FollowItem
    from ..collector.context import ContextBasedPerformTemplate, ContextCollector
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


class LookupBranch(TypedDict, Generic[T]):
    metadata: LookupBranchMetadata
    levels: LookupCollection
    artifacts: dict[Any, TargetArtifactStore[T]]


class TargetArtifactStore(TypedDict, Generic[T]):
    collector: ContextCollector
    entity: T
    pattern: list[_FollowItem]


LookupBranches: TypeAlias = "dict[str | FollowsPredicater | None, LookupBranch]"
LookupCollection: TypeAlias = "dict[str, LookupBranches]"


class TargetEntityProtocol(Protocol[P, T]):
    def get_collect_signature(self, entity: T, *args: P.args, **kwargs: P.kwargs) -> Any:
        ...

    def __post_collected__(self, artifact: TargetArtifactStore[T]):
        ...


class TargetFn(
    Fn[Concatenate[Selectable, P], R],
):
    def __init__(self, template: Callable[Concatenate[C, P], R]) -> None:
        self.template = template  # type: ignore

    def collect(
        self: TargetEntityProtocol[P1, T],  # type: ignore
        collector: ContextCollector,
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

    def _iter_branches(
        self: TargetEntityProtocol[P1, T], collections: list[MutableMapping[Any, Any]], target: Selector
    ) -> Generator[LookupBranch[T], Any, None]:
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
        self, entity: Callable[Concatenate[ContextBasedPerformTemplate, "Selector", P], R]
    ) -> Any:
        return FnImplement(self.capability, self.name)

    def get_artifact_record(
        self, runner: Context, target: Selectable, *args: P.args, **kwargs: P.kwargs
    ) -> tuple[ContextCollector, Callable[Concatenate[ContextBasedPerformTemplate, Selector, P], R]]:
        sign = FnImplement(self.capability, self.name)
        for branch in self._iter_branches(runner.artifacts.maps, target.to_selector()):
            artifacts = branch["artifacts"]
            if sign in artifacts:
                return artifacts[sign]["collector"], artifacts[sign]["entity"]
        raise NotImplementedError(f"no {repr(self)} implements for {target.to_selector()}.")

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__
