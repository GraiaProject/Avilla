from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from graia.broadcast.entities.event import Dispatchable

T = TypeVar("T")
P = TypeVar("P")


class AbstractEventParser(Generic[T, P], metaclass=ABCMeta):
    parsers: dict[T, Callable[[P, Any], Awaitable[Any]]] = {}

    def __init_subclass__(cls, **kwargs):
        cls.parsers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, AbstractEventParser):
                cls.parsers.update(base.parsers)

    @abstractmethod
    def key(self, token: Any) -> T:
        raise NotImplementedError

    async def parse(self, protocol: P, raw_data: Any) -> Dispatchable | None:
        key = self.key(raw_data)
        for pattern, parser in self.parsers.items():
            if pattern == key:
                return await parser(protocol, raw_data)
