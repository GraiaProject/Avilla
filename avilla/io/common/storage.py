from abc import ABCMeta, abstractmethod
from datetime import timedelta
from typing import Any, Generic, List, TypeVar

from avilla.core.service import ExportInterface

D = TypeVar("D")


class Storage(ExportInterface):
    pass


"""
class KVStorage(Storage):
    @abstractmethod
    async def get(self, key: str, default: Any = None) -> Any:
        ...

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        ...

    @abstractmethod
    async def delete(self, key: str, strict: bool = False) -> None:
        ...

    @abstractmethod
    async def clear(self) -> None:
        ...

    @abstractmethod
    async def has(self, key: str) -> bool:
        ...
"""
# TODO: still in progress (design)


class CacheStorage(Storage, Generic[D], metaclass=ABCMeta):
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

    @abstractmethod
    async def has(self, key: str) -> bool:
        ...

    @abstractmethod
    async def keys(self) -> List[str]:
        ...