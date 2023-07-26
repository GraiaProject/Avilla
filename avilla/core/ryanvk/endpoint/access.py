from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Union

from .protocol import Endpoint

if TYPE_CHECKING:
    from avilla.core.ryanvk.collector.base import PerformTemplate


T = TypeVar("T")


class Access(Endpoint[T]):
    def evaluate(self, instance: PerformTemplate) -> T:
        return instance.components[self.name]

    @staticmethod
    def optional():
        return OptionalAccess()


class OptionalAccess(Endpoint[Union[T, None]]):
    def evaluate(self, instance: PerformTemplate) -> T | None:
        return instance.components.get(self.name)
