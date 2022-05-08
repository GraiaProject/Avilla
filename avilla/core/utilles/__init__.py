from __future__ import annotations

import asyncio
import random
import string
from types import TracebackType
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
)

from graia.broadcast import BaseDispatcher, DispatcherInterface
from graia.broadcast.utilles import Ctx, run_always_await_safely


def random_string(k: int = 12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))


def as_async(func):
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

class Defer:
    _ctx: Ctx[List[Callable[[], Any]] | None] = Ctx("defer")

    @classmethod
    def current(cls):
        return cls(cls._ctx.get(None) or [])

    def __init__(self, defers: List[Callable[[], Any]]) -> None:
        self.defers = defers

    def add(self, defer: Callable[[], Any]) -> None:
        self.defers.append(defer)


class DeferDispatcher(BaseDispatcher):
    async def beforeExecution(self, interface: DispatcherInterface):
        interface.local_storage["defers"] = []
        interface.local_storage["defers_ctxtoken"] = Defer._ctx.set(interface.local_storage["defers"])

    async def catch(self, interface: DispatcherInterface):
        if interface.annotation is Defer:
            return Defer(interface.local_storage["defers"])

    async def afterExecution(
        self, interface: DispatcherInterface, exception: Optional[Exception], tb: Optional[TracebackType]
    ):
        await asyncio.gather(*[run_always_await_safely(defer) for defer in interface.local_storage["defers"]])
        Defer._ctx.reset(interface.local_storage["defers_ctxtoken"])


T = TypeVar("T")


class Registrar(Dict):
    def register(self, key):
        def decorator(method):
            self[key] = method
            return method

        return decorator

    def decorate(self, attr):
        def decorator(cls: Type[T]) -> Type[T]:
            getattr(cls, attr).update(self)
            return cls

        return decorator


async def as_asynciter(iter: Iterable[T]) -> AsyncGenerator[T, None]:
    for item in iter:
        yield item
