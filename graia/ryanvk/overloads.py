from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet, Any, MutableSet

from ryanvk._ordered_set import OrderedSet
from ryanvk.typing import Twin

from .fn.overload import FnOverload


@dataclass(eq=True, frozen=True)
class SimpleOverloadSignature:
    value: Any


class SimpleOverload(FnOverload[SimpleOverloadSignature, type[Any], Any]):
    def digest(self, collect_value: Any) -> SimpleOverloadSignature:
        return SimpleOverloadSignature(collect_value)

    def collect(self, scope: dict, signature: SimpleOverloadSignature) -> MutableSet[Twin]:
        if signature.value not in scope:
            target = scope[signature.value] = OrderedSet()
        else:
            target = scope[signature.value]

        return target

    def harvest(self, scope: dict, value: Any) -> AbstractSet[Twin]:
        if value in scope:
            return scope[value]

        return set()

    def track(self, scope: dict, signature: SimpleOverloadSignature) -> MutableSet[Twin]:
        return scope[signature]


@dataclass(eq=True, frozen=True)
class TypeOverloadSignature:
    type: type[Any]


class TypeOverload(FnOverload[TypeOverloadSignature, type[Any], Any]):
    def digest(self, collect_value: type) -> TypeOverloadSignature:
        return TypeOverloadSignature(collect_value)

    def collect(self, scope: dict, signature: TypeOverloadSignature) -> MutableSet[Twin]:
        if signature.type not in scope:
            target = scope[signature.type] = OrderedSet()
        else:
            target = scope[signature.type]

        return target

    def harvest(self, scope: dict, value: Any) -> AbstractSet[Twin]:
        t = type(value)
        if t in scope:
            return scope[t]

        return set()

    def track(self, scope: dict, signature: TypeOverloadSignature) -> MutableSet[Twin]:
        return scope[signature.type]


class _SingletonOverloadSignature:
    ...


SINGLETON_SIGN = _SingletonOverloadSignature()


class SingletonOverload(FnOverload[None, None, None]):
    def digest(self, collect_value: None) -> _SingletonOverloadSignature:
        return SINGLETON_SIGN

    def collect(self, scope: dict, signature: _SingletonOverloadSignature) -> MutableSet[Twin]:
        s = scope[None] = set()
        return s

    def harvest(self, scope: dict, value: None) -> AbstractSet[Twin]:
        return scope[None]

    def track(self, scope: dict, signature: None) -> MutableSet[Twin]:
        return scope[None]
