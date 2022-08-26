from __future__ import annotations

from asyncio import Future
from contextlib import suppress
from typing import Generic, TypeVar

T = TypeVar("T")

class Stream(Generic[T]):
    _receivers: list[Future[T]]
    closed: bool = False

    def __init__(self) -> None:
        self._receivers = []

    async def __iter__(self):
        if self.closed:
            raise RuntimeError("stream was closed.")
        while not self.closed:
            future = Future()
            self._receivers.append(future)
            try:
                yield await future
            finally:
                with suppress(ValueError):
                    self._receivers.remove(future)

    def push(self, value: T):
        for receiver in self._receivers:
            if not receiver.done() and not receiver.cancelled():
                receiver.set_result(value)

    def close(self):
        self.closed = True
        for receiver in self._receivers:
            if not receiver.done() and not receiver.cancelled():
                receiver.cancel()
