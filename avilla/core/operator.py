import fnmatch
from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from datetime import timedelta
from functools import partial
from typing import Any, AsyncIterable, Dict, Generic, List, Optional, Tuple, TypeVar

from avilla.core.service.entity import Status
from avilla.core.utilles import random_string
from avilla.io.common.storage import CacheStorage

from .selectors import resource as resource_selector

TContent = TypeVar("TContent")


class OperatorCache(Generic[TContent], metaclass=ABCMeta):
    @abstractmethod
    async def get(self, key: str, default: Any = None) -> TContent:
        ...

    @abstractmethod
    async def set(self, key: str, value: TContent) -> None:
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


class OperatorKeyDispatch(Operator):
    patterns: Dict[str, Operator]

    def __init__(self, patterns: Dict[str, Operator]):
        self.patterns = patterns

    async def operate(
        self, operator: str, target: Any, value: Any = None, cache: OperatorCache = None
    ) -> Any:
        if not isinstance(target, str):
            raise TypeError("target must be a string (like a key)")
        for pattern, op in self.patterns.items():
            if fnmatch.fnmatch(target, pattern):
                return await op.operate(operator, target, value, cache)
        raise KeyError(f"cannot dispatch for target '{target}'")

    def __getattr__(self, name: str):
        return partial(self.operate, name)


# TODO: 缓存智能失效：放在 Protocol 里面，能获取所有 Operator Cache 管控的缓存类型，
# 且能够在 MetadataChanged 事件触发，且 key match 时智能取消相应的缓存。


class PatchedCache(OperatorCache):
    cache: CacheStorage
    keys: List[str]
    prefix: str

    def __init__(self, cache: CacheStorage, prefix: str = "") -> None:
        self.cache = cache
        self.prefix = prefix
        self.keys = []

    async def get(self, key: str, default: Any = None) -> Any:
        return await self.cache.get(self.prefix + key, default)

    async def set(self, key: str, value: Any) -> None:
        await self.cache.set(self.prefix + key, value)
        self.keys.append(key)

    async def delete(self, key: str, strict: bool = False) -> None:
        await self.cache.delete(self.prefix + key, strict)
        self.keys.remove(key)

    async def clear(self) -> None:
        for key in self.keys:
            await self.cache.delete(self.prefix + key)

    async def has(self, key: str) -> bool:
        return await self.cache.has(self.prefix + key)

    @classmethod
    @asynccontextmanager
    async def patch(cls, cache: CacheStorage):
        instance = cls(cache)
        yield instance
        await instance.clear()


class OperatorCachePatcher(Operator):
    operator: Operator
    prefix: str
    cache: PatchedCache

    def __init__(self, operator: Operator, cache: CacheStorage) -> None:
        self.operator = operator
        self.prefix = random_string()
        self.cache = PatchedCache(cache, self.prefix)

    async def operate(self, operator: str, target: Any, value: Any = None, _=None) -> Any:
        return await self.operator.operate(operator, target, value, self.cache)

    def __getattr__(self, name: str):
        return partial(self.operate, name)


# 以后用 cast + OperatorCachePatcher + OperatorDispatch 就好了。
# 什么？你问我这下面两个是什么？两个拿来 type hint 的。
# 然后哈哈，想起来还有个缓存智能失效。焯！


class MetadataOperator(Operator):
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


class ResourceOperator(Operator):
    resource: resource_selector

    async def create(self, id: resource_selector = None) -> Status:
        return await self.operate("create", id, None)

    async def write(self, data: Any, id: resource_selector = None) -> Status:
        return await self.operate("write", id, data)

    async def put(self, data: Any) -> Tuple[Status, Optional[resource_selector]]:
        return await self.operate("put", None, data)

    async def read(self, id: resource_selector = None) -> Tuple[Status, Optional[Any]]:
        return await self.operate("read", id, None)

    async def stats(self, id: resource_selector = None) -> Status:
        return await self.operate("stats", id, None)

    async def ls(
        self, parent: Optional[resource_selector] = None
    ) -> Tuple[Status, AsyncIterable[resource_selector]]:
        return await self.operate("ls", parent, None)

    async def cover(self, to: resource_selector, id: resource_selector = None) -> Status:
        return await self.operate("rename", id, to)

    async def remove(
        self,
        id: resource_selector = None,
    ) -> Status:
        return await self.operate("remove", id, None)

    async def meta(self, id: resource_selector = None) -> Tuple[Status, Optional[MetadataOperator]]:
        return await self.operate("meta", id, None)
