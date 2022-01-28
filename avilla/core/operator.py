import fnmatch
from abc import ABCMeta, abstractmethod
from datetime import timedelta
from functools import partial
from typing import Any, AsyncIterable, Dict, Generic, Optional, Tuple, TypeVar

from avilla.core.service.entity import Status
from avilla.io.common.storage import CacheStorage

from .selectors import resource as resource_selector

TContent = TypeVar("TContent")


class OperatorCache(Generic[TContent], metaclass=ABCMeta):
    @abstractmethod
    async def get(self, key: str, default: Any = None) -> TContent:
        ...

    @abstractmethod
    async def set(self, key: str, value: TContent, expire: timedelta = None) -> None:
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


class Operator(metaclass=ABCMeta):
    @abstractmethod
    async def operate(self, operator: str, target: Any, value: Any, cache: OperatorCache = None) -> Any:
        ...


class OperatorDispatch(Operator):
    patterns: Dict[str, Operator]

    def __init__(self, patterns: Dict[str, Operator]):
        self.patterns = patterns

    async def operate(self, operator: str, target: Any, value: Any, cache: OperatorCache = None) -> Any:
        if not isinstance(target, str):
            raise TypeError("target must be a string (like a key)")
        for pattern, op in self.patterns.items():
            if fnmatch.fnmatch(target, pattern):
                return await op.operate(target, operator, value, cache)
        raise KeyError(f"cannot dispatch for target '{target}'")

    def __getattr__(self, name: str):
        return partial(self.operate, operator=name)


class Metadata(Operator):
    async def get(self, key: str) -> Any:
        return await self.operate("get", key, None)

    async def set(self, key: str, value: Any) -> None:
        await self.operate("set", key, value)

    async def reset(self, key: str) -> None:
        await self.operate("reset", key, None)

    async def prev(self, key: str) -> Any:
        return await self.operate("prev", key, None)

    async def next(self, key: str) -> Any:
        return await self.operate("next", key, None)

    async def push(self, key: str, value: Any) -> None:
        await self.operate("push", key, value)

    async def pop(self, key: str, index: int) -> Any:
        return await self.operate("pop", key, index)

    async def add(self, key: str, value: Any) -> None:
        await self.operate("add", key, value)

    async def remove(self, key: str, value: Any) -> None:
        await self.operate("remove", key, value)


class Resource(Operator):
    async def create(self, id: resource_selector) -> Status:
        return await self.operate("create", id, None)

    async def write(self, id: resource_selector, data: Any) -> Status:
        return await self.operate("write", id, data)

    async def put(self, data: Any) -> Tuple[Status, Optional[resource_selector]]:
        return await self.operate("put", None, data)

    async def read(self, id: resource_selector) -> Tuple[Status, Optional[Any]]:
        return await self.operate("read", id, None)

    async def stats(self, id: resource_selector) -> Status:
        return await self.operate("stats", id, None)

    async def ls(
        self, parent: Optional[resource_selector] = None
    ) -> Tuple[Status, AsyncIterable[resource_selector]]:
        return await self.operate("ls", parent, None)

    async def cover(self, id: resource_selector, to: resource_selector) -> Status:
        return await self.operate("rename", id, to)

    async def remove(
        self,
        id: resource_selector,
    ) -> Status:
        return await self.operate("remove", id, None)

    async def meta(self, id: resource_selector) -> Tuple[Status, Optional[Metadata]]:
        return await self.operate("meta", id, None)
