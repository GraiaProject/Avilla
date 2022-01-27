from abc import ABCMeta, abstractmethod
import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Callable, ClassVar, Dict, Set, Type, TypeVar, Union, overload

from graia.broadcast.utilles import run_always_await_safely
from avilla.core.service.entity import Activity

from avilla.core.service.session import BehaviourSession
from avilla.core.selectors import resource as resource_selector
from avilla.core.typing import META_OPS, METADATA_VALUE


class ResourceProvider(metaclass=ABCMeta):
    supported_resource_types: ClassVar[Set[str]]

    @abstractmethod
    @asynccontextmanager
    def access_resource(self, res: resource_selector) -> AsyncGenerator[BehaviourSession, None]:
        ...

    @abstractmethod
    async def resource_meta_operate(
        self, res: resource_selector, metakey: str, operator: META_OPS, value: METADATA_VALUE
    ) -> Any:
        ...


class ResourceMetaWrapper:
    resource: resource_selector
    provider: ResourceProvider

    def __init__(self, res: resource_selector, provider: ResourceProvider) -> None:
        self.resource = res
        self.provider = provider

    async def get(self, metakey: str) -> Any:
        return await self.provider.resource_meta_operate(self.resource, metakey, "get", None)

    async def set(self, metakey: str, value: Any) -> None:
        return await self.provider.resource_meta_operate(self.resource, metakey, "set", value)

    async def reset(self, metakey: str) -> None:
        return await self.provider.resource_meta_operate(self.resource, metakey, "reset", None)

    async def next(self, metakey: str) -> Any:
        return await self.provider.resource_meta_operate(self.resource, metakey, "next", None)

    async def push(self, metakey: str, value: Any) -> None:
        return await self.provider.resource_meta_operate(self.resource, metakey, "push", value)

    async def pop(self, metakey: str, index: int) -> Any:
        return await self.provider.resource_meta_operate(self.resource, metakey, "pop", index)

    async def add(self, metakey: str, value: Any) -> None:
        return await self.provider.resource_meta_operate(self.resource, metakey, "add", value)

    async def remove(self, metakey: str, value: Any) -> None:
        return await self.provider.resource_meta_operate(self.resource, metakey, "remove", value)


TActivityHandler = Callable[[Union[Activity, None]], Union[Awaitable[Any], Any]]


class ResourceAccessor:
    activity_handlers: Dict[Type[Activity], TActivityHandler]

    def __init__(
        self,
        activity_handlers: Dict[Type[Activity], TActivityHandler],
    ) -> None:
        self.activity_handlers = activity_handlers
    if TYPE_CHECKING:
        R = TypeVar("R")

        @overload
        async def execute(self, activity: Type[Activity[R]]) -> R:
            pass

        @overload
        async def execute(self, activity: Activity[R]) -> R:
            pass

        async def execute(self, activity: ...) -> Any:
            ...

    else:
        async def execute(self, activity: Union[Type[Activity], Activity]):
            activity_class = activity if isinstance(activity, type) else type(activity)
            handler = self.activity_handlers.get(activity_class)
            if handler is None:
                raise NotImplementedError(f"No handler for activity {activity_class}")
            return await run_always_await_safely(handler, activity if not isinstance(activity, type) else None)

    async def execute_all(self, *activities: Union[Type[Activity], Activity]):
        return await asyncio.gather(*[self.execute(activity) for activity in activities])

    def is_allowed(self, activity_type: Type[Activity]) -> bool:
        return activity_type in self.activity_handlers
