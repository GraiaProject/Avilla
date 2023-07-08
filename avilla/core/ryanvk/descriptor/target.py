from __future__ import annotations

import inspect
import itertools
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Generic,
    Iterable,
    MutableMapping,
    Protocol,
)

from typing_extensions import Concatenate, ParamSpec, TypeAlias, TypeVar

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.selector import FollowsPredicater, Selectable, Selector, _parse_follows
from avilla.core.utilles import identity

from .base import Fn, FnImplement

if TYPE_CHECKING:
    from ..collector.base import BaseCollector, PerformTemplate
    from ..runner import Runner


T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R", covariant=True)
Q = TypeVar("Q", contravariant=True)
VnCallable = TypeVar("VnCallable", bound="Callable")
VnCollector = TypeVar("VnCollector", bound="BaseCollector", default="BaseCollector")
VnRunner = TypeVar("VnRunner", bound="Runner", default="Runner")
HQ = TypeVar("HQ", bound="PerformTemplate", contravariant=True)

HnPerform = Callable[Concatenate[HQ, Selector, P], R]


@dataclass
class LookupBranchMetadata:
    override: bool


@dataclass
class LookupBranch(Generic[T, VnCollector]):
    metadata: LookupBranchMetadata
    levels: LookupCollection[T, VnCollector]
    artifacts: dict[Any, TargetArtifactStore[T, VnCollector]]


@dataclass
class TargetArtifactStore(Generic[Q, VnCollector]):
    collector: VnCollector
    entity: Q


LookupBranches: TypeAlias = "dict[str | FollowsPredicater | None, LookupBranch[T, VnCollector]]"
LookupCollection: TypeAlias = "dict[str, LookupBranches[T, VnCollector]]"
PerformBranch: TypeAlias = "LookupBranch[HnPerform[HQ, P, R], VnCollector]"
PerformCollection: TypeAlias = "LookupCollection[HnPerform[HQ, P, R], VnCollector]"


class TargetConcatenateOutbound(Protocol[P, R]):
    def __call__(self, target: Selectable, *args: P.args, **kwargs: P.kwargs) -> R:
        ...


class TargetFn(
    Generic[P, R, VnCollector, VnRunner],
    Fn[TargetConcatenateOutbound[P, Any], VnCollector, VnRunner],
):
    def __init__(self, template: Callable[Concatenate[Any, P], R]) -> None:
        self.template = template

    def get_collect_signature(self, collector: VnCollector, pattern: str, **kwargs: FollowsPredicater):
        return FnImplement(self.capability, self.name)

    def get_collect_layout(self, collector: VnCollector, pattern: str, **kwargs: FollowsPredicater):
        items = _parse_follows(pattern, **kwargs)
        if not items:
            raise ValueError("invalid target pattern")

        collection: PerformCollection[Any, P, R, VnCollector] = collector.artifacts["current_collection"]

        if TYPE_CHECKING:
            branch: PerformBranch[Any, P, R, VnCollector] = LookupBranch(LookupBranchMetadata(True), {}, {})

        for i in items:
            if i.name not in collection:
                collection[i.name] = {}

            branches = collection[i.name]

            if (i.literal or i.predicate) in branches:
                branch = branches[i.literal or i.predicate]
            else:
                branch = LookupBranch(LookupBranchMetadata(True), {}, {})
                branches[i.literal or i.predicate] = branch
            collection = branch.levels

        return branch

    def collect(self, collector: VnCollector, pattern: str, **kwargs: FollowsPredicater):
        def receive(entity: Callable[Concatenate[HQ, Selector, P], R]):
            branch = self.get_collect_layout(collector, pattern, **kwargs)
            signature = self.get_collect_signature(collector, pattern, **kwargs)
            artifact = TargetArtifactStore(collector, entity)
            branch.artifacts[signature] = artifact
            return entity

        return receive

    def _iter_branches(
        self, artifact_collections: list[MutableMapping[Any, Any]], target: Selector
    ) -> Generator[LookupBranch[HnPerform[HQ, P, R], VnCollector], Any, None]:
        lookups: Iterable[PerformCollection[Any, P, R, VnCollector]] = itertools.chain(
            *[i["lookup_collections"] for i in artifact_collections if "lookup_collections" in i]
        )

        for collection in lookups:
            # get branch
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
                        if not header(v):
                            break
                    else:
                        if None not in branches:
                            break
                        header = None

                branch = branches[header]
                collection = branch.levels
                if header is not None:
                    if branch.metadata.override and None in branches:
                        collection = {**(branches[None].levels), **collection}
            if branch is None:
                continue

            yield branch

    def get_artifact_record(
        self: TargetFn[P, R, VnCollector, VnRunner],
        runner: VnRunner,
        target: Selectable,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[VnCollector, Callable[Concatenate[Any, Selector, P], R]]:
        sign = FnImplement(self.capability, self.name)
        select = target.to_selector()
        for branch in self._iter_branches(runner.artifacts.maps, select):
            if sign in branch.artifacts:
                artifact = branch.artifacts[sign]
                return artifact.collector, artifact.entity
        raise NotImplementedError(f"no {repr(self)} implements for {select}.")

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__
