from contextlib import AsyncExitStack
from functools import cached_property, partial
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    List,
    Optional,
    Type,
    TypedDict,
    TypeVar,
    Union,
    cast,
    overload,
)
import weakref

from avilla.core.context import ctx_eventmeta
from avilla.core.execution import Execution
from avilla.core.metadata import Metadata, MetadataModifies
from avilla.core.resource import Resource
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import request as request_selector
from avilla.core.typing import TExecutionMiddleware
from avilla.core.utilles import Defer, random_string
from avilla.core.utilles.selector import Selector
from avilla.io.common.storage import CacheStorage

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


class ExecutorWrapper:
    relationship: "Relationship"
    execution: "Execution"
    middlewares: List[TExecutionMiddleware]

    def __init__(self, relationship: "Relationship") -> None:
        self.relationship = relationship
        self.middlewares = relationship.protocol.avilla.exec_middlewares.copy()

    def __await__(self):
        return self.ensure().__await__()

    async def ensure(self):
        async with AsyncExitStack() as stack:
            for middleware in reversed(self.middlewares):
                await stack.enter_async_context(middleware(self.relationship, self.execution))  # type: ignore
            return await self.relationship.protocol.ensure_execution(self.execution)

    def execute(self, execution: "Execution"):
        self.execution = execution
        return self

    __call__ = execute

    def to(self, target: Union[entity_selector, mainline_selector]):
        self.execution.locate_target(target)
        return self

    def use(self, middleware: TExecutionMiddleware):
        self.middlewares.append(middleware)
        return self


M = TypeVar("M", entity_selector, mainline_selector, request_selector, Selector)

_T = TypeVar("_T")
_M = TypeVar("_M", bound=Metadata)


class PatchedCache:
    cache: CacheStorage
    keys: List[str]
    prefix: str
    # 指从接收到的 event 中获取的 meta, 用于 event parsing -> relationship meta 这二层的单向透传

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
        if self.has(key):
            await self.cache.delete(self.prefix + key, strict)
            self.keys.remove(key)

    async def clear(self) -> None:
        for key in self.keys:
            await self.cache.delete(self.prefix + key)

    async def has(self, key: str) -> bool:
        return await self.cache.has(self.prefix + key)


class Relationship(Generic[M]):
    ctx: M
    mainline: mainline_selector
    current: entity_selector
    via: Optional[Union[entity_selector, mainline_selector]]
    cache: PatchedCache

    protocol: "BaseProtocol"

    _middlewares: List[TExecutionMiddleware]

    def __init__(
        self,
        protocol: "BaseProtocol",
        ctx: M,
        mainline: mainline_selector,
        current: entity_selector,
        via: Optional[Union[mainline_selector, entity_selector, None]] = None,
        middlewares: Optional[List[TExecutionMiddleware]] = None,
    ) -> None:
        self.ctx = ctx
        self.mainline = mainline
        self.via = via
        self.current = current
        self.protocol = protocol
        self._middlewares = middlewares or []
        
        cache = self.protocol.avilla.get_interface(CacheStorage)
        if cache:
            self.cache = PatchedCache(cache, random_string())
            weakref.finalize(self, self.protocol.avilla.broadcast.loop.create_task, self.cache.clear())

    @property
    def exec(self):
        return ExecutorWrapper(self)

    @overload
    async def complete(self, selector: mainline_selector) -> mainline_selector:
        ...

    @overload
    async def complete(self, selector: entity_selector) -> entity_selector:
        ...

    async def complete(self, selector: ...) -> ...:
        if isinstance(selector, mainline_selector):
            tempdict = self.mainline.path.copy()
            tempdict.update(selector.path)
            return self.protocol.complete_selector(mainline_selector(tempdict))
        elif isinstance(selector, entity_selector):
            if "mainline" not in selector.path:
                selector.path['mainline'] = self.mainline
            return self.protocol.complete_selector(selector)
        else:
            raise TypeError(f"{selector} is not a supported selector for rs.complete.")

    async def fetch(self, resource: Resource[_T]) -> _T:
        # TODO: rs.fetch
        pass

    @overload
    async def meta(self, target: Type[_M]) -> _M:
        ...

    @overload
    async def meta(self, target: MetadataModifies[_T]) -> _T:
        ...

    async def meta(self, target: ...) -> ...:
        if issubclass(target, Metadata):
            return await self.protocol.fetch_metadata(self, target)
        elif isinstance(target, MetadataModifies):
            return await self.protocol.modify_metadata(self, target)
        else:
            raise TypeError("unknown operation")