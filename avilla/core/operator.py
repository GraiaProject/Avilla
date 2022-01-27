import fnmatch
from abc import ABCMeta, abstractmethod
from datetime import timedelta

from avilla.core.service.entity import Status
from .selectors import resource as resource_selector
from typing import Any, AsyncIterable, Dict, Generic, Optional, Tuple, TypeVar

from avilla.core.service.common.storage import CacheStorage

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
    async def operate(self, target: Any, operator: str, value: Any, cache: OperatorCache = None) -> Any:
        ...


class OperatorDispatch(Operator):
    operators: Dict[str, Operator]

    def __init__(self, operators: Dict[str, Operator]):
        self.operators = operators

    async def operate(self, target: Any, operator: str, value: Any, cache: OperatorCache = None) -> Any:
        if not isinstance(target, str):
            raise TypeError("target must be a string (like a key)")
        for pattern, op in self.operators.items():
            if fnmatch.fnmatch(target, pattern):
                return await op.operate(target, operator, value, cache)
        raise KeyError(f"cannot dispatch for target {target}")

class Metadata(Operator):
    async def get(self, key: str) -> Any:
        return await self.operate(key, "get", None)

    async def set(self, key: str, value: Any) -> None:
        await self.operate(key, "set", value)

    async def reset(self, key: str) -> None:
        await self.operate(key, "reset", None)

    async def prev(self, key: str) -> Any:
        return await self.operate(key, "prev", None)

    async def next(self, key: str) -> Any:
        return await self.operate(key, "next", None)

    async def push(self, key: str, value: Any) -> None:
        await self.operate(key, "push", value)

    async def pop(self, key: str, index: int) -> Any:
        return await self.operate(key, "pop", index)

    async def add(self, key: str, value: Any) -> None:
        await self.operate(key, "add", value)

    async def remove(self, key: str, value: Any) -> None:
        await self.operate(key, "remove", value)


class Resource(Operator):
    async def create(self, id: resource_selector) -> Status:
        return await self.operate(id, "create", None)
    
    async def write(self, id: resource_selector, data: Any) -> Status:
        return await self.operate(id, "write", data)
    
    async def put(self, data: Any) -> Tuple[Status, Optional[resource_selector]]:
        return await self.operate(None, "put", data)
    
    async def read(self, id: resource_selector) -> Tuple[Status, Optional[Any]]:
        return await self.operate(id, "read", None)
    
    async def stats(self, id: resource_selector) -> Status:
        return await self.operate(id, "stats", None)
    
    async def ls(self, parent: Optional[resource_selector] = None) -> Tuple[Status, AsyncIterable[resource_selector]]:
        return await self.operate(parent, "ls", None)
    
    async def cover(self, id: resource_selector, to: resource_selector) -> Status:
        return await self.operate(id, "rename", to)

    async def remove(self, id: resource_selector,) -> Status:
        return await self.operate(id, "remove", None)

    async def meta(self, id: resource_selector) -> Tuple[Status, Optional[Metadata]]:
        return await self.operate(id, "meta", None)
