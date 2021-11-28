from inspect import iscoroutinefunction
from typing import Any, Callable, Generic, List, TypeVar

from graia.broadcast.utilles import run_always_await_safely

T = TypeVar("T")


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
        return result

    def unwrap_sync(self) -> T:
        result = self.content
        for wrapper in self.wrappers:
            if iscoroutinefunction(wrapper):
                raise RuntimeError("Cannot unwrap a stream with a coroutine transformer in sync")
            result = wrapper(result)
        return result

    def transform(self, transformer: Callable[[Any], Any]):
        self.wrappers.append(transformer)
        return self
