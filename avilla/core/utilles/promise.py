from __future__ import annotations

from asyncio import Future
from contextlib import suppress
from typing import Generic, TypeVar

T = TypeVar("T")


class Promise(Generic[T]):
    _futures: list[Future[T]]
    done: bool = False

    def __init__(self) -> None:
        self._futures = []

    def __await__(self):
        return self.__await_impl__().__await__()

    async def __await_impl__(self):
        future = Future()
        try:
            self._futures.append(future)
            return await future
        finally:
            with suppress(ValueError):
                self._futures.remove(future)

    def resolve(self, value: T):
        for future in self._futures:
            if not future.done() and not future.cancelled():
                future.set_result(value)

    def reject(self, exception: Exception):
        for future in self._futures:
            if not future.done() and not future.cancelled():
                future.set_exception(exception)

    def cancel(self):
        for future in self._futures:
            if not future.done() and not future.cancelled():
                future.cancel()
