from abc import ABCMeta, abstractmethod
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, TypeVar

from graia.broadcast import Dispatchable

from avilla.core.message import Element

T = TypeVar("T")
P = TypeVar("P")


class AbstractEventParser(Generic[T, P], metaclass=ABCMeta):
    parsers: Dict[T, Callable[[P, Any], Awaitable[Any]]] = {}

    def __init_subclass__(cls, **kwargs):
        cls.parsers = {}
        for base in reversed(cls.__bases__):
            if issubclass(base, AbstractEventParser):
                cls.parsers.update(base.parsers)

    @abstractmethod
    def key(self, token: Any) -> T:
        raise NotImplementedError

    async def parse(self, protocol: P, raw_data: Any) -> Optional[Dispatchable]:
        key = self.key(raw_data)
        for pattern, parser in self.parsers.items():
            if pattern == key:
                return await parser(protocol, raw_data)
