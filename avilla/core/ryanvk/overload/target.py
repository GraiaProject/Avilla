from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
)

from typing_extensions import TypeAlias, TypeVar

from avilla.core.selector import FollowsPredicater, Selector, _parse_follows
from graia.ryanvk.collector import BaseCollector
from graia.ryanvk.overload import FnOverload

T = TypeVar("T")

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

class TargetOverload(FnOverload):
    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, str],
    ) -> None:
        record = (collector, entity)

        for param, pattern_str in params.items():
            param_scope = scope.setdefault(param, {})

            pattern_items = _parse_follows(pattern_str)
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

            processing_scope: LookupCollection = scope[arg_name]

            branch = None
            for key, value in selector.pattern.items():
                if (branches := processing_scope.get(key)) is None:
                    raise NotImplementedError
                
                if value in branches:
                    header = value
                else:
                    for header, branch in branches.items():
                        if callable(header) and header(value):
                            break
                    else:  # hit wildcard
                        if None not in branches:
                            break
                        header = None

                branch = branches[header]
                processing_scope = branch.levels

                if header is not None and None in branches:
                    processing_scope = branches[None].levels | processing_scope
            else:
                # this time, match finished, maybe branch
                if branch is not None and branch.bind:
                    # branch has bind
                    bind_sets.append(branch.bind)
                    break

            raise NotImplementedError
        
        return bind_sets.pop().intersection(*bind_sets)

    def merge_scopes(self, *scopes: dict[Any, Any]):
        # scope layout: {
        #   <param_name: str>: LookupCollection
        # }
        ...  # TODO