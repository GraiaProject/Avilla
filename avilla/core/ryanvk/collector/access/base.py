from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
    overload,
)

from typing_extensions import Self

if TYPE_CHECKING:
    from avilla.core.ryanvk.collector.base import PerformTemplate


T = TypeVar("T")


class Access(Generic[T]):
    name: str

    def __init__(self):
        ...

    def __set_name__(self, owner: type, name: str):
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self:
        ...

    @overload
    def __get__(self, instance: PerformTemplate, owner: type) -> T:
        ...

    def __get__(self, instance: PerformTemplate | None, owner: type):
        if instance is None:
            return self

        return instance.components[self.name]

    @staticmethod
    def optional():
        return OptionalAccess()


class OptionalAccess(Access[T]):
    @overload
    def __get__(self, instance: None, owner: type) -> Self:
        ...

    @overload
    def __get__(self, instance: PerformTemplate, owner: type) -> T | None:
        ...

    def __get__(self, instance: PerformTemplate | None, owner: type):
        if instance is None:
            return self

        return instance.components.get(self.name)
