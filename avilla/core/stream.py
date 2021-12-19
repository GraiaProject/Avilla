from inspect import iscoroutinefunction
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    List,
    TypeVar,
    cast,
    overload,
)

from graia.broadcast.utilles import run_always_await_safely

T = TypeVar("T")
V = TypeVar("V")


class Stream(Generic[T]):
    content: T
    wrappers: List[Callable[[Any], Any]]

    def __init__(self, initial: T) -> None:
        self.content = initial
        self.wrappers = []

    async def unwrap(self) -> T:
        result = self.content
        for wrapper in self.wrappers:
            result = await run_always_await_safely(wrapper, result)
        return cast(T, result)

    def unwrap_sync(self) -> T:
        result = self.content
        for wrapper in self.wrappers:
            if iscoroutinefunction(wrapper):
                raise RuntimeError("Cannot unwrap a stream with a coroutine transformer in sync")
            result = wrapper(result)
        return cast(T, result)

    if TYPE_CHECKING:

        @overload
        def transform(self, wrapper: Callable[[T], V]) -> "Stream[V]":
            ...

        @overload
        def transform(self, wrapper: Callable[[T], Awaitable[V]]) -> "Stream[V]":
            ...

        def transform(self, wrapper: Callable[[T], Any]) -> "Stream[T]":
            ...

    else:

        def transform(self, transformer):
            self.wrappers.append(transformer)
            return self

    __or__ = transform

    def __await__(self):
        return self.unwrap().__await__()
