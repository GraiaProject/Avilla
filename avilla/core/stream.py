from typing import Awaitable, Callable, Generic, TypeVar


T = TypeVar("T")
R = TypeVar("R")


class Stream(Generic[T]):
    content: T

    def __init__(self, initial: T) -> None:
        self.content = initial

    def unwrap(self) -> T:
        return self.content

    async def transform(self, transformer: Callable[[T], Awaitable[R]]) -> "Stream[R]":
        return Stream(await transformer(self.content))
