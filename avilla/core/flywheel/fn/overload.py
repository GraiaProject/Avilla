from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
    overload,
)
from typing_extensions import Self, final

from .record import FnOverloadHarvest
from ..typing import Twin

if TYPE_CHECKING:
    from .compose import FnCompose

TOverload = TypeVar("TOverload", bound="FnOverload", covariant=True)
TCallValue = TypeVar("TCallValue")
TCollectValue = TypeVar("TCollectValue")
TSignature = TypeVar("TSignature")


class FnOverload(Generic[TSignature, TCollectValue, TCallValue]):
    def __init__(self) -> None:
        ...

    @final
    def as_agent(self):
        return FnOverloadAgentDescriptor(self)

    def digest(self, collect_value: TCollectValue) -> TSignature:
        ...

    def collect(self, scope: dict, signature: TSignature) -> dict[Twin, None]:
        ...

    def harvest(self, scope: dict, value: TCallValue) -> dict[Twin, None]:
        ...

    def access(self, scope: dict, signature: TSignature) -> dict[Twin, None] | None:
        ...


class FnOverloadAgent(Generic[TOverload]):
    name: str
    compose: FnCompose
    fn_overload: TOverload

    def __init__(self, name: str, fn: FnCompose, overload: TOverload):
        self.name = name
        self.compose = fn
        self.fn_overload = overload

    def collect(self: FnOverloadAgent[FnOverload[Any, TCollectValue, Any]], value: TCollectValue):
        return FnOverloadHarvest(self.name, self.fn_overload, value)

    def call(self: FnOverloadAgent[FnOverload[Any, Any, TCallValue]], value: TCallValue):
        return FnOverloadHarvest(self.name, self.fn_overload, value)


class FnOverloadAgentDescriptor(Generic[TOverload]):
    name: str
    fn_overload: TOverload

    def __init__(self, fn_overload: TOverload) -> None:
        self.fn_overload = fn_overload

    def __set_name__(self, name: str, owner: type):
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self:
        ...

    @overload
    def __get__(self, instance: FnCompose, owner: type) -> FnOverloadAgent[TOverload]:
        ...

    def __get__(self, instance: FnCompose | None, owner: type):
        if instance is None:
            return self

        return FnOverloadAgent(self.name, instance, self.fn_overload)
