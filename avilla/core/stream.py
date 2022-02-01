from inspect import iscoroutinefunction
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    cast,
    overload,
)

from graia.broadcast.utilles import run_always_await_safely

T = TypeVar("T")
V = TypeVar("V")


class Stream(Generic[T]):
    content: T
    wrappers: List[Tuple[Callable[[Any], Any], Optional[Type]]]

    def __init__(self, initial: T) -> None:
        self.content = initial
        self.wrappers = []

    async def unwrap(self) -> T:
        result = self.content
        for wrapper, assert_type in self.wrappers:
            if assert_type is not None and not isinstance(result, assert_type):
                continue
            result = await run_always_await_safely(wrapper, result)
        return cast(T, result)

    def unwrap_sync(self) -> T:
        result = self.content
        for wrapper, assert_type in self.wrappers:
            if iscoroutinefunction(wrapper):
                raise RuntimeError("Cannot unwrap a stream with a coroutine transformer in sync")
            if assert_type is not None and not isinstance(result, assert_type):
                continue
            result = wrapper(result)
        return cast(T, result)

    if TYPE_CHECKING:

        @overload
        def transform(self, wrapper: "Callable[[T], V]") -> "Stream[V]":
            ...

        @overload
        def transform(self, wrapper: "Callable[[T | V], V]", assert_type: Optional[Type[T]] = None) -> "Stream[T]":
            ...

        @overload
        def transform(self, wrapper: "Callable[[T], Awaitable[V]]") -> "Stream[V]":
            ...
        
        @overload
        def transform(self, wrapper: "Callable[[T | V], Awaitable[V]]", assert_type: Optional[Type[T]] = None) -> "Stream[T]":
            ...

        def transform(self, wrapper: "Callable[[T], Any]", assert_type: Optional[Type[T]] = None) -> "Stream[Any]":
            ...

    else:

        def transform(self, transformer, assert_type: Optional[Type[T]] = None) -> "Stream[T]":
            self.wrappers.append((transformer, assert_type))
            return self

    __or__ = transform

    def __await__(self):
        return self.unwrap().__await__()
