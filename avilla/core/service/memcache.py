import asyncio
from datetime import timedelta
from heapq import heappush, heappop
from time import time
from typing import Type, Any, List, Tuple, Dict, Optional, NoReturn

from avilla.core import Service, LaunchComponent, TInterface
from avilla.core.selectors import entity as entity_selector
from avilla.core.service.common.cache import CacheInterface, D
from avilla.core.utilles import as_async


class MemCache(CacheInterface):
    cache: Dict[str, Tuple[Optional[float], D]]
    expire: List[Tuple[float, str]]

    def __init__(self, cache: Dict[str, Tuple[Optional[float], D]], expire: List[Tuple[float, str]]):
        self.cache = cache
        self.expire = expire

    async def get(self, key: str, default: Any = None) -> D:
        value = self.cache.get(key)
        if value:
            if value[0] is None or value[0] >= time():
                return value[1]
            else:
                del self.cache[key]
        return default

    async def set(self, key: str, value: Any, expire: timedelta = None) -> None:
        if expire is None:
            self.cache[key] = (None, value)
            return

        expire_time = time() + expire.total_seconds()
        self.cache[key] = (expire_time, value)
        heappush(self.expire, (expire_time, value))

    async def delete(self, key: str, strict: bool = False) -> None:
        if strict:
            del self.cache[key]
        self.cache.pop(key, None)

    async def clear(self) -> None:
        for key, value in self.cache.items():
            if value[0] <= time():
                del self.cache[key]

    async def has(self, key: str) -> bool:
        return key in self.cache


class MemCacheService(Service):
    supported_interface_types = {MemCache, CacheInterface}
    supported_description_types = set()

    interval: float
    cache: Dict[str, Tuple[Optional[float], D]]
    expire: List[Tuple[float, str]]
    _expire_cycle: asyncio.Task = None

    def __init__(
        self,
        interval: float = 0.1,
        cache: Dict[str, Tuple[Optional[float], D]] = None,
        expire: List[Tuple[float, str]] = None,
    ):
        self.interval = interval
        self.cache = cache if cache else {}
        self.expire = expire if expire else []
        super().__init__()

    def get_interface(self, interface_type: Type[TInterface]) -> TInterface:
        if issubclass(interface_type, (MemCache, CacheInterface)):
            return MemCache(self.cache, self.expire)
        raise ValueError(f"unsupported interface type {interface_type}")

    def get_status(self, entity: entity_selector = None):
        if entity is None:
            return self.status
        if entity not in self.status:
            raise KeyError(f"{entity} not in status")
        return self.status[entity]

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            "cache.client",
            set(),
            prepare=lambda _: self.expire_cycle,
            cleanup=lambda _: as_async(self.expire_cycle.close)(),
        )

    @property
    async def expire_cycle(self) -> asyncio.Task:
        if self._expire_cycle is None:

            async def cycle() -> NoReturn:
                while True:
                    expire_time, key = self.expire[0]
                    while expire_time <= time():
                        self.cache.pop(key, None)
                        heappop(self.expire)
                        expire_time, key = self.expire[0]
                    await asyncio.sleep(self.interval)

            self._expire_cycle = asyncio.create_task(cycle())
        return self._expire_cycle
