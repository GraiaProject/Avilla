from typing import Awaitable, Callable, Generic, TypeVar


T = TypeVar("T")
R = TypeVar("R")


class Stream(Generic[T]):
    content: T

    def __init__(self, initial: T) -> None:
        self.content = initial

    def unwrap(self) -> T:
        return self.content

    def transform(self, transformer: Callable[[T], R]) -> "Stream[R]":
        return Stream(transformer(self.content))
