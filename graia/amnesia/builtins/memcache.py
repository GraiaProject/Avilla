from __future__ import annotations

import asyncio
from datetime import timedelta
from heapq import heappop, heappush
from time import time
from typing import Any

from launart import Launart, Service

from graia.amnesia.transport.common.storage import CacheStorage


class Memcache(CacheStorage[Any]):
    cache: dict[str, tuple[float | None, Any]]
    expire: list[tuple[float, str]]

    def __init__(
        self,
        cache: dict[str, tuple[float | None, Any]],
        expire: list[tuple[float, str]],
    ):
        self.cache = cache
        self.expire = expire

    async def get(self, key: str, default: Any = None) -> Any:
        value = self.cache.get(key)
        if value:
            if value[0] is None or value[0] >= time():
                return value[1]
            del self.cache[key]
        return default

    async def set(self, key: str, value: Any, expire: timedelta | None = None) -> None:
        if expire is None:
            self.cache[key] = (None, value)
        else:
            expire_time = time() + expire.total_seconds()
            self.cache[key] = (expire_time, value)
            heappush(self.expire, (expire_time, key))

    async def delete(self, key: str, strict: bool = False) -> None:
        if strict or key in self.cache:
            del self.cache[key]

    async def clear(self) -> None:
        self.cache.clear()
        self.expire.clear()

    async def has(self, key: str) -> bool:
        return key in self.cache

    async def keys(self) -> list[str]:
        return list(self.cache.keys())


class MemcacheService(Service):
    id = "cache.client/memcache"
    supported_interface_types = {Memcache}, {CacheStorage: 10}

    interval: float
    cache: dict[str, tuple[float | None, Any]]
    expire: list[tuple[float, str]]

    def __init__(
        self,
        interval: float = 0.1,
        cache: dict[str, tuple[float | None, Any]] | None = None,
        expire: list[tuple[float, str]] | None = None,
    ):
        self.interval = interval
        self.cache = cache or {}
        self.expire = expire or []
        super().__init__()

    def get_interface(self, _) -> Memcache:
        return Memcache(self.cache, self.expire)

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, manager: Launart) -> None:
        async with self.stage("blocking"):
            while not manager.status.exiting:
                while self.expire and self.expire[0][0] <= time():
                    _, key = heappop(self.expire)
                    self.cache.pop(key, None)
                await asyncio.sleep(self.interval)
