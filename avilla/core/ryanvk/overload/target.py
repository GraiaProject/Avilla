from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, AbstractSet, Any, Callable, Literal, Mapping, MutableSet, Union

from typing_extensions import TypeAlias

from avilla.core.selector import _FollowItem, FollowsPredicater, Selector, _parse_follows
from graia.ryanvk.collector import BaseCollector
from graia.ryanvk import FnOverload

from graia.ryanvk.typing import Twin


TargetScopeRoot: TypeAlias = dict[str, 'TargetScopeBranch']

@dataclass
class TargetScopeHit:
    store: MutableSet[Twin]
    children: TargetScopeRoot


@dataclass
class TargetScopeBranch:
    literal: dict[str, TargetScopeHit]
    predicator: dict[FollowsPredicater, TargetScopeHit]


@dataclass(eq=True, frozen=True)
class TargetOverloadSignature:
    pattern: tuple[_FollowItem, ...]


class TargetOverload(FnOverload[TargetOverloadSignature, str, Selector]):
    def digest(self, collect_value: str) -> TargetOverloadSignature:
        return TargetOverloadSignature((*_parse_follows(collect_value),))

    def collect(self, scope: TargetScopeRoot, signature: TargetOverloadSignature) -> MutableSet[Twin]:
        processing = scope
        target = None
        
        for item in signature.pattern:
            target = None
            if item.name not in processing:
                processing[item.name] = TargetScopeBranch({}, {})
            
            branch = processing[item.name]
            
            if item.literal is not None:
                if item.literal not in branch.literal:
                    branch.literal[item.literal] = TargetScopeHit(set(), {})

                target = branch.literal[item.literal]
            elif item.predicate is not None:
                if item.predicate not in branch.predicator:
                    branch.predicator[item.predicate] = TargetScopeHit(set(), {})

                target = branch.predicator[item.predicate]
            else:
                assert target is not None

            processing = target.children
        
        assert target is not None
        
        return target.store

    def harvest(self, scope: TargetScopeRoot, value: Selector) -> AbstractSet[Twin]:
        processing = scope
        store = None
        
        for lhs, rhs in value.items():
            if lhs not in processing:
                return frozenset()
        
            branch = processing[lhs]
            if rhs in branch.literal:
                hit = branch.literal[rhs]
            else:
                for predicator, hit in branch.predicator.items():
                    if predicator(rhs):
                        break
                else:
                    if '*' in branch.literal:
                        hit = branch.literal['*']
                    else:
                        return frozenset()

            processing = hit.children
            store = hit.store
        
        if store is None:
            return frozenset()

        return store
