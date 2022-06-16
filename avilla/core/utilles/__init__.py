from __future__ import annotations

import asyncio
import random
import string
from collections import ChainMap
from collections.abc import (
    AsyncGenerator,
    Callable,
    Generator,
    Iterable,
    Iterator,
    Mapping,
)
from typing import TYPE_CHECKING, Any, TypeVar

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.utilles import Ctx, run_always_await_safely

if TYPE_CHECKING:
    from types import TracebackType

    from graia.broadcast.interfaces.dispatcher import DispatcherInterface


def random_string(k: int = 12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))


def as_async(func):
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class Defer:
    _ctx: Ctx[list[Callable[[], Any]] | None] = Ctx("defer")

    @classmethod
    def current(cls):
        return cls(cls._ctx.get(None) or [])

    def __init__(self, defers: list[Callable[[], Any]]) -> None:
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
        self, interface: DispatcherInterface, exception: Exception | None, tb: TracebackType | None
    ):
        await asyncio.gather(*[run_always_await_safely(defer) for defer in interface.local_storage["defers"]])
        Defer._ctx.reset(interface.local_storage["defers_ctxtoken"])


T = TypeVar("T")


class Registrar(dict):
    def register(self, key):
        def decorator(method):
            self[key] = method
            return method

        return decorator

    def decorate(self, attr):
        def decorator(cls: type[T]) -> type[T]:
            getattr(cls, attr).update(self)
            return cls

        return decorator


async def as_asynciter(iter: Iterable[T]) -> AsyncGenerator[T, None]:
    for item in iter:
        yield item


def as_generator(iter: Iterable[T]) -> Generator[T, None, None]:
    yield from iter


_K = TypeVar("_K")
_V = TypeVar("_V")
_D = TypeVar("_D")


class LayeredChain(Mapping[_K, _V]):
    def __init__(self, *groups: Iterable[dict[_K, _V]]):
        self.groups = groups

    def _floor_gen(self):
        generators = [as_generator(i) for i in self.groups]
        while True:
            m = map(lambda x: next(x, None), generators)
            n = [i for i in m if i is not None]
            if not n:
                break
            yield n

    def _iter_floor_chain(self):
        for floor in self._floor_gen():
            yield ChainMap(*floor)

    def __getitem__(self, __k: _K) -> _V:
        for chain_map in self._iter_floor_chain():
            if __k in chain_map:
                return chain_map[__k]
        raise KeyError(__k)

    def __iter__(self):
        for chain_map in self._iter_floor_chain():
            yield from chain_map.keys()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.groups})"

    def __str__(self):
        return f"{self.__class__.__name__}({self.groups})"

    def __contains__(self, __k: _K) -> bool:
        return any(__k in chain_map for chain_map in self._iter_floor_chain())

    def get(self, __k: _K, default: _V | _D = None) -> _V | _D:
        for chain_map in self._iter_floor_chain():
            if __k in chain_map:
                return chain_map[__k]
        return default

    def items(self) -> Iterator[tuple[_K, _V]]:
        for chain_map in self._iter_floor_chain():
            yield from chain_map.items()

    def keys(self) -> Iterator[_K]:
        for chain_map in self._iter_floor_chain():
            yield from chain_map.keys()

    def values(self) -> Iterator[_V]:
        for chain_map in self._iter_floor_chain():
            yield from chain_map.values()
