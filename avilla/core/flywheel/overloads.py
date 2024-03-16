from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Type

from .fn.overload import FnOverload


@dataclass(eq=True, frozen=True)
class SimpleOverloadSignature:
    value: Any


class SimpleOverload(FnOverload[SimpleOverloadSignature, Any, Any]):
    def digest(self, collect_value: Any) -> SimpleOverloadSignature:
        return SimpleOverloadSignature(collect_value)

    def collect(self, scope: dict, signature: SimpleOverloadSignature) -> dict[Callable, None]:
        if signature.value not in scope:
            target = scope[signature.value] = {}
        else:
            target = scope[signature.value]

        return target

    def harvest(self, scope: dict, call_value: Any) -> dict[Callable, None]:
        if call_value in scope:
            return scope[call_value]

        return {}

    def access(self, scope: dict, signature: SimpleOverloadSignature) -> dict[Callable, None] | None:
        if signature.value in scope:
            return scope[signature.value]


@dataclass(eq=True, frozen=True)
class TypeOverloadSignature:
    type: type[Any]


class TypeOverload(FnOverload[TypeOverloadSignature, Type[Any], Any]):
    def digest(self, collect_value: type) -> TypeOverloadSignature:
        return TypeOverloadSignature(collect_value)

    def collect(self, scope: dict, signature: TypeOverloadSignature) -> dict[Callable, None]:
        if signature.type not in scope:
            target = scope[signature.type] = {}
        else:
            target = scope[signature.type]

        return target

    def harvest(self, scope: dict, call_value: Any) -> dict[Callable, None]:
        t = type(call_value)
        if t in scope:
            return scope[t]

        return {}

    def access(self, scope: dict, signature: TypeOverloadSignature) -> dict[Callable, None] | None:
        if signature.type in scope:
            return scope[signature.type]


class _SingletonOverloadSignature:
    ...


SINGLETON_SIGN = _SingletonOverloadSignature()


class SingletonOverload(FnOverload[_SingletonOverloadSignature, None, None]):
    SIGNATURE = SINGLETON_SIGN

    def digest(self, collect_value) -> _SingletonOverloadSignature:
        return SINGLETON_SIGN

    def collect(self, scope: dict, signature) -> dict[Callable, None]:
        s = scope[None] = {}
        return s

    def harvest(self, scope: dict, call_value) -> dict[Callable, None]:
        return scope[None]

    def access(self, scope: dict, signature) -> dict[Callable, None] | None:
        if None in scope:
            return scope[None]


SINGLETON_OVERLOAD = SingletonOverload("singleton")
