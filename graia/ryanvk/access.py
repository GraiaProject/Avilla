from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Union

from .endpoint import Endpoint

if TYPE_CHECKING:
    from .perform import BasePerform


T = TypeVar("T")


class Access(Endpoint[T], dynamic=False):
    def evaluate(self, instance: BasePerform) -> T:
        return instance.staff.components[self.name]

    @staticmethod
    def optional():
        return OptionalAccess()


class OptionalAccess(Endpoint[Union[T, None]], dynamic=False):
    def evaluate(self, instance: BasePerform) -> T | None:
        return instance.staff.components.get(self.name)
