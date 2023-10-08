from __future__ import annotations

from contextlib import asynccontextmanager
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Generic,
    TypeVar,
    overload,
)

from typing_extensions import Self

if TYPE_CHECKING:
    from graia.ryanvk.perform import BasePerform


T = TypeVar("T")


class Endpoint(Generic[T]):
    __dynamic__: ClassVar[bool] = False

    name: str

    def __init__(self):
        ...

    def __set_name__(self, owner: type[BasePerform], name: str):
        if self.__dynamic__ and owner.__static__:
            raise TypeError(f"{self.__class__.__name__} conflicts with static perform {owner.__name__}")

        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self:
        ...

    @overload
    def __get__(self, instance: BasePerform, owner: type) -> T:
        ...

    def __get__(self, instance: BasePerform | None, owner: type):
        if instance is None:
            return self

        return self.evaluate(instance)

    def __init_subclass__(cls, *, dynamic: bool) -> None:
        return super().__init_subclass__()

    def evaluate(self, instance: BasePerform) -> T:
        ...

    @asynccontextmanager
    async def lifespan(self, instance: BasePerform):
        yield
