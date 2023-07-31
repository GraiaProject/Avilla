from __future__ import annotations

import inspect
import itertools
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ChainMap,
    Generator,
    Generic,
    Iterable,
    MutableMapping,
    Protocol,
)

from typing_extensions import Concatenate, ParamSpec, TypeAlias, TypeVar

from avilla.core.selector import FollowsPredicater, Selectable, Selector, _parse_follows
from avilla.core.utilles import identity

from .base import Fn, FnImplement

if TYPE_CHECKING:
    from avilla.core.ryanvk.collector.base import BaseCollector, PerformTemplate


T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R", covariant=True)
Q = TypeVar("Q", contravariant=True)
VnCallable = TypeVar("VnCallable", bound="Callable")
HQ = TypeVar("HQ", bound="PerformTemplate", contravariant=True)

HnPerform = Callable[Concatenate[HQ, Selector, P], R]


@dataclass
class LookupBranchMetadata:
    ...


@dataclass
class LookupBranch(Generic[T]):
    metadata: LookupBranchMetadata
    levels: LookupCollection[T]
    artifacts: dict[Any, TargetArtifactStore[T]]


@dataclass
class TargetArtifactStore(Generic[Q]):
    collector: BaseCollector
    entity: Q


LookupBranches: TypeAlias = "dict[str | FollowsPredicater | None, LookupBranch[T]]"
LookupCollection: TypeAlias = "dict[str, LookupBranches[T]]"
PerformBranch: TypeAlias = "LookupBranch[HnPerform[HQ, P, R]]"
PerformCollection: TypeAlias = "LookupCollection[HnPerform[HQ, P, R]]"


class TargetConcatenateOutbound(Protocol[P, R]):
    def __call__(self, target: Selectable, *args: P.args, **kwargs: P.kwargs) -> R:
        ...


class TargetFn(
    Fn[TargetConcatenateOutbound[P, R]],
):
    def __init__(self, template: Callable[Concatenate[Any, P], R]) -> None:
        self.template = template

    def get_collect_signature(self, collector: BaseCollector, pattern: str, **kwargs: FollowsPredicater):
        return FnImplement(self.capability, self.name)

    def get_collect_layout(self, collector: BaseCollector, pattern: str, **kwargs: FollowsPredicater):
        items = _parse_follows(pattern, **kwargs)
        if not items:
            raise ValueError("invalid target pattern")

        collection: PerformCollection[Any, P, R] = collector.artifacts["current_collection"]

        if TYPE_CHECKING:
            branch: PerformBranch[Any, P, R] = LookupBranch(LookupBranchMetadata(), {}, {})

        for i in items:
            if i.name not in collection:
                collection[i.name] = {}

            branches = collection[i.name]

            if (i.literal or i.predicate) in branches:
                branch = branches[i.literal or i.predicate]
            else:
                branch = LookupBranch(LookupBranchMetadata(), {}, {})
                branches[i.literal or i.predicate] = branch
            collection = branch.levels

        return branch

    def collect(
        self: TargetFn[P, R], collector: BaseCollector, pattern: str, **kwargs: FollowsPredicater
    ) -> Callable[[Callable[Concatenate[HQ, Selector, P], R]], Callable[Concatenate[HQ, Selector, P], R]]:
        def receive(entity):
            branch = self.get_collect_layout(collector, pattern, **kwargs)
            signature = self.get_collect_signature(collector, pattern, **kwargs)
            artifact = TargetArtifactStore(collector, entity)
            branch.artifacts[signature] = artifact
            return entity

        return receive

    def _iter_branches(
        self, artifact_collections: list[MutableMapping[Any, Any]], target: Selector
    ) -> Generator[LookupBranch[HnPerform[HQ, P, R]], Any, None]:
        lookups: Iterable[PerformCollection[Any, P, R]] = itertools.chain.from_iterable(
            i["lookup_collections"] for i in artifact_collections if "lookup_collections" in i
        )

        for collection in lookups:
            branch = None
            for key, value in target.pattern.items():
                if (branches := collection.get(key)) is None:
                    break

                if value in branches:  # hit literal
                    header = value
                else:
                    for header, branch in branches.items():  # hit predicate
                        if callable(header) and header(value):
                            break
                    else:  # hit wildcard
                        if None not in branches:
                            break
                        header = None

                branch = branches[header]
                collection = branch.levels

                if header is not None and None in branches:
                    collection = branches[None].levels | collection

            if branch is not None:
                yield branch

    def get_artifact_signature(
        self: TargetFn[P, R],
        collection: ChainMap[Any, Any],
        target: Selectable,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        return FnImplement(self.capability, self.name)

    def get_artifact_record(
        self: TargetFn[P, R],
        collection: ChainMap[Any, Any],
        target: Selectable,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[BaseCollector, Callable[Concatenate[Any, Selector, P], R]]:
        sign = self.get_artifact_signature(collection, target, *args, **kwargs)
        select = target.to_selector()
        for branch in self._iter_branches(collection.maps, select):
            if sign in branch.artifacts:
                artifact = branch.artifacts[sign]
                return artifact.collector, artifact.entity
        raise NotImplementedError(f"no {repr(self)} implements for {select}.")

    def __repr__(self) -> str:
        return f"<Fn#target {identity(self.capability)}::{self.name} {inspect.Signature.from_callable(self.template)}>"

    __str__ = __repr__
