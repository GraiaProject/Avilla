from datetime import timedelta
from typing import Any, Type, Union

from aioredis import Redis

from avilla.core.launch import LaunchComponent
from avilla.core.service import Service
from avilla.core.service.common.cache import CacheInterface


class RedisCache(CacheInterface):
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


class RedisService(Service):
    supported_interface_types = {RedisCache, CacheInterface}
    supported_description_types = set()

    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_interface(self, interface_type: Union[Type[RedisCache], Type[CacheInterface]]):
        if issubclass(interface_type, (RedisCache, CacheInterface)):
            return RedisCache(self.redis)
        raise ValueError(f"unsupported interface type {interface_type}")

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            "cache.client",
            set(),
            prepare=lambda _: self.redis.initialize(),
            cleanup=lambda _: self.redis.close(),
        )
