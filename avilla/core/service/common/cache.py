from abc import ABCMeta, abstractmethod
from datetime import timedelta
from typing import Any, Generic, TypeVar

from avilla.core.service import ExportInterface

D = TypeVar("D")


class CacheInterface(ExportInterface, Generic[D], metaclass=ABCMeta):
    @abstractmethod
    async def get(self, key: str, default: Any = None) -> D:
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, expire: timedelta = None) -> None:
        ...

    @abstractmethod
    async def delete(self, key: str, strict: bool = False) -> None:
        ...

    @abstractmethod
    async def clear(self) -> None:
        ...
