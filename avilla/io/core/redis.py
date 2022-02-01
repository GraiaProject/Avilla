from datetime import timedelta
from typing import Any, Dict, List, Type, Union

from aioredis import Redis

from avilla.core.launch import LaunchComponent
from avilla.core.selectors import entity as entity_selector
from avilla.core.service import Service, Status
from avilla.io.common.storage import CacheStorage


class RedisCache(CacheStorage):
    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str, default: Any = None) -> Any:
        return await self.redis.get(key) or default

    async def set(self, key: str, value: Any, expire: timedelta = None) -> None:
        await self.redis.set(key, value)
        if expire:
            await self.redis.expire(key, int(expire.total_seconds()))

    async def delete(self, key: str, strict: bool = False) -> None:
        await self.redis.delete(key)

    async def clear(self) -> None:
        await self.redis.flushall()

    async def has(self, key: str) -> bool:
        return await self.redis.exists(key)

    async def keys(self) -> List[str]:
        return await self.redis.keys()


class RedisService(Service):
    supported_interface_types = {RedisCache, CacheStorage}
    supported_description_types = set()

    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis
        super().__init__()

    def get_interface(self, interface_type: Union[Type[RedisCache], Type[CacheStorage]]):
        if issubclass(interface_type, (RedisCache, CacheStorage)):
            return RedisCache(self.redis)
        raise ValueError(f"unsupported interface type {interface_type}")

    def get_status(self, entity: entity_selector = None) -> Union[Status, Dict[entity_selector, Status]]:
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
            prepare=lambda _: self.redis.initialize(),
            cleanup=lambda _: self.redis.close(),
        )
