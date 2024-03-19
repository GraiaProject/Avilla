from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

from flywheel.fn.overload import FnOverload
from typing_extensions import TypeAlias

from avilla.core.selector import FollowsPredicater, Selector, _parse_follows


@dataclass
class LookupBranchMetadata: ...


@dataclass
class LookupBranch:
    metadata: LookupBranchMetadata
    levels: LookupCollection
    bind: dict[Callable, None] = field(default_factory=dict)


LookupBranches: TypeAlias = "dict[str | FollowsPredicater | None, LookupBranch]"
LookupCollection: TypeAlias = "dict[str, LookupBranches]"


@dataclass
class TargetOverloadSignature:
    order: str
    predicators: dict[str, FollowsPredicater] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(("TOS", self.order, tuple(self.predicators.items())))


class TargetOverload(FnOverload[TargetOverloadSignature, tuple[str, dict[str, FollowsPredicater]], Selector]):
    def digest(self, collect_value: tuple[str, dict[str, FollowsPredicater]]) -> TargetOverloadSignature:
        return TargetOverloadSignature(collect_value[0], collect_value[1])

    def collect(self, scope: dict, signature: TargetOverloadSignature) -> dict[Callable, None]:
        pattern_items = _parse_follows(signature.order)
        if not pattern_items:
            raise ValueError("invalid target pattern")

        processing_level = scope

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

        return branch.bind

    def harvest(self, scope: dict, value: Selector) -> dict[Callable, None]:
        processing_scope: LookupCollection = scope
        branch = None

        for k, v in value.pattern.items():
            if (branches := processing_scope.get(k)) is None:
                return {}

            if v in branches:
                header = v
            else:
                for _key, branch in branches.items():
                    if callable(_key) and _key(v):
                        header = _key
                        break  # hit predicate
                else:
                    if None in branches:
                        header = None  # hit default
                    elif "*" in branches:
                        return branches["*"].bind  # hit wildcard
                    else:
                        return {}

            branch = branches[header]
            processing_scope = branch.levels
            if header is not None and None in branches:
                processing_scope = branches[None].levels | processing_scope

        if branch is not None and branch.bind:
            return branch.bind
        else:
            return {}

    def access(self, scope: dict, signature: TargetOverloadSignature) -> dict[Callable, None] | None:
        pattern_items = _parse_follows(signature.order)
        if not pattern_items:
            raise ValueError("invalid target pattern")

        processing_level = scope

        if TYPE_CHECKING:
            branch = LookupBranch(LookupBranchMetadata(), {})

        for item in pattern_items:
            if item.name not in processing_level:
                return

            branches: LookupBranches = processing_level[item.name]
            if (item.literal or item.predicate) not in branches:
                return

            branch = branches[item.literal or item.predicate]
            processing_level = branch.levels

        return branch.bind
