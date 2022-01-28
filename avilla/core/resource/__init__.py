from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterable,
    ClassVar,
    Optional,
    Set,
    Tuple,
)

from avilla.core.operator import Metadata, Operator, OperatorCache
from avilla.core.service.entity import Status

from avilla.core.selectors import resource as resource_selector
from avilla.core.typing import METADATA_VALUE


class ResourceProvider(metaclass=ABCMeta):
    supported_resource_types: ClassVar[Set[str]]

    @abstractmethod
    @asynccontextmanager
    def access_resource(self, res: resource_selector) -> AsyncGenerator["ResourceOperator", None]:
        ...

    @abstractmethod
    async def resource_meta_operate(
        self,
        res: resource_selector,
        metakey: str,
        operator: str,
        value: METADATA_VALUE,
        cache: Optional[OperatorCache] = None,
    ) -> Any:
        ...


class ResourceOperator(Operator):
    resource: resource_selector
    provider: "ResourceProvider"

    def __init__(self, resource: resource_selector, provider: "ResourceProvider") -> None:
        self.resource = resource
        self.provider = provider

    async def operate(self, operator: str, target: Any, value: Any, cache: OperatorCache = None) -> Any:
        return await self.provider.resource_meta_operate(self.resource, operator, target, value, cache)

    async def create(self) -> Status:
        return await self.operate("create", self.resource, None)

    async def write(self, data: Any) -> Status:
        return await self.operate("write", self.resource, data)

    async def put(self, data: Any) -> Tuple[Status, Optional[resource_selector]]:
        return await self.operate("put", None, data)

    async def read(self) -> Tuple[Status, Optional[Any]]:
        return await self.operate("read", self.resource, None)

    async def stats(self) -> Status:
        return await self.operate("stats", self.resource, None)

    async def ls(
        self
    ) -> Tuple[Status, AsyncIterable[resource_selector]]:
        return await self.operate("ls", self.resource, None)

    async def cover(self, to: resource_selector) -> Status:
        return await self.operate("rename", self.resource, to)

    async def remove(self) -> Status:
        return await self.operate("remove", self.resource, None)

    async def meta(self) -> Tuple[Status, Optional[Metadata]]:
        return await self.operate("meta", self.resource, None)
