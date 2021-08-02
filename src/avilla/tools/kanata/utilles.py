from typing import Any, Iterable, List

from types import TracebackType
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    NamedTuple,
    Optional,
    Tuple,
    Literal,
    Union,
)
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from enum import IntEnum


class InsertGenerator:
    base: Iterable[Any]
    insert_items: List[Any]

    def __init__(self, base_iterable: Iterable, pre_items: List[Any] = None) -> None:
        self.base = base_iterable
        self.insert_items = pre_items or []

    def __iter__(self):
        for i in self.base:
            if self.insert_items:
                yield self.insert_items.pop()
            yield i
        else:
            if self.insert_items:
                yield from self.insert_items[::-1]


class StatusCodeEnum(IntEnum):
    DISPATCHING = 1

    DISPATCH_COMPLETED = 2
    EXECUTION_COMPLETED = 3

    DISPATCH_EXCEPTION = 4
    EXECUTION_EXCEPTION = 5


class ResponseCodeEnum(IntEnum):
    VALUE = 1


class ExcInfo(NamedTuple):
    exception: Exception
    traceback: TracebackType


T_AsyncDispatcherContextManager = AsyncGenerator[
    Union[None, Tuple[Literal[ResponseCodeEnum.VALUE], Any]],
    Union[None, Tuple[StatusCodeEnum, Union[ExcInfo]]],
]


class AsyncDispatcherContextManager(BaseDispatcher):
    generator_factory: Callable[[Any], T_AsyncDispatcherContextManager]
    generator: T_AsyncDispatcherContextManager
    ready: bool = False

    def __init__(self, generator_factory: Callable, args=None, kwargs=None) -> None:
        self.generator_factory = generator_factory
        self.args = args or ()
        self.kwargs = kwargs or {}

    async def beforeExecution(self, interface: "DispatcherInterface"):
        self.generator = self.generator_factory(*self.args, **self.kwargs)
        await self.generator.__anext__()
        await self.generator.asend(interface)
        self.ready = True

    async def catch(self, interface: "DispatcherInterface"):
        if not self.ready:
            return
        status, value = await self.generator.asend((StatusCodeEnum.DISPATCHING, None))
        if status is ResponseCodeEnum.VALUE:
            return value

    async def afterDispatch(
        self,
        interface: "DispatcherInterface",
        exception: Optional[Exception],
        tb: Optional[TracebackType],
    ):
        self.ready = False
        try:
            if not tb:
                await self.generator.asend((StatusCodeEnum.DISPATCH_COMPLETED, None))
            else:
                await self.generator.asend((StatusCodeEnum.DISPATCH_EXCEPTION, ExcInfo(exception, tb)))
        except StopIteration:
            pass

    async def afterExecution(
        self,
        interface: "DispatcherInterface",
        exception: Optional[Exception],
        tb: Optional[TracebackType],
    ):
        try:
            if not tb:
                await self.generator.asend((StatusCodeEnum.EXECUTION_COMPLETED, None))
            else:
                await self.generator.asend((StatusCodeEnum.EXECUTION_EXCEPTION, ExcInfo(exception, tb)))
        except StopIteration:
            pass
