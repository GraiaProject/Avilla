from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from typing_extensions import TypeAlias

from avilla.core.selector import FollowsPredicater, Selector, _parse_follows
from graia.ryanvk.collector import BaseCollector
from graia.ryanvk.overload import FnOverload


@dataclass
class LookupBranchMetadata:
    ...


@dataclass
class LookupBranch:
    metadata: LookupBranchMetadata
    levels: LookupCollection
    bind: set[tuple[BaseCollector, Callable]] = field(default_factory=set)


LookupBranches: TypeAlias = "dict[str | FollowsPredicater | None, LookupBranch]"
LookupCollection: TypeAlias = "dict[str, LookupBranches]"


@dataclass
class TargetOverloadConfig:
    pattern: str
    predicators: dict[str, FollowsPredicater]

    def __init__(self, pattern: str, **predicators: FollowsPredicater):
        self.pattern = pattern
        self.predicators = predicators


def _merge_lookup_collection(current: LookupCollection, other: LookupCollection):
    for key, branches in current.items():
        if (other_branches := other.pop(key, None)) is None:
            continue

        for header, branch in branches.items():
            if (other_branch := other_branches.pop(header, None)) is None:
                continue

            _merge_lookup_collection(branch.levels, other_branch.levels)
            branch.bind |= other_branch.bind

        branches |= other_branches

    current |= other


class TargetOverload(FnOverload):
    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, str | TargetOverloadConfig],
    ) -> None:
        record = (collector, entity)

        for param, pattern in params.items():
            param_scope = scope.setdefault(param, {})

            if isinstance(pattern, str):
                pattern = TargetOverloadConfig(pattern)

            pattern_items = _parse_follows(pattern.pattern, **pattern.predicators)
            if not pattern_items:
                raise ValueError("invalid target pattern")

            processing_level = param_scope

            if TYPE_CHECKING:
                branch = LookupBranch(LookupBranchMetadata(), {})

            for item in pattern_items:
                if item.name not in processing_level:
                    processing_level[item.name] = {}

                branches = processing_level[item.name]
                if (item.literal or item.predicate) in branches:
                    branch = branches[item.literal or item.predicate]
                else:
                    branch = LookupBranch(LookupBranchMetadata(), {})
                    branches[item.literal or item.predicate] = branch

                processing_level = branch.levels

            branch.bind.add(record)

    def get_entities(self, scope: dict[Any, Any], args: dict[str, Selector]) -> set[tuple[BaseCollector, Callable]]:
        bind_sets: list[set] = []

        for arg_name, selector in args.items():
            if arg_name not in scope:
                raise NotImplementedError

            def get_bind_set():
                processing_scope: LookupCollection = scope[arg_name]
                branch = None
                for key, value in selector.pattern.items():
                    if (branches := processing_scope.get(key)) is None:
                        raise NotImplementedError

                    if value in branches:
                        header = value
                    else:
                        for _key, branch in branches.items():
                            if callable(_key) and _key(value):
                                header = _key
                                break  # hit predicate
                        else:
                            if None in branches:
                                header = None  # hit default
                            elif "*" in branches:
                                return branches["*"].bind  # hit wildcard
                            else:
                                raise NotImplementedError

                    branch = branches[header]
                    processing_scope = branch.levels

                    if header is not None and None in branches:
                        processing_scope = branches[None].levels | processing_scope
                if branch is not None and branch.bind:
                    # branch has bind
                    return branch.bind

                raise NotImplementedError

            bind_sets.append(get_bind_set())
        return bind_sets.pop().intersection(*bind_sets)

    def merge_scopes(self, *scopes: dict[Any, Any]):
        # scope layout: {
        #   <param_name: str>: LookupCollection
        # }
        param_collections: dict[str, list[LookupCollection]] = {}
        result = {}

        for scope in scopes:
            for param, collection in scope.items():
                param_collections.setdefault(param, []).append(collection)

        for param, collections in param_collections.items():
            result[param] = current = collections.pop(0)
            for other in collections:
                _merge_lookup_collection(current, other)

        return result
