from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from inspect import isawaitable
from typing import Any, Generic, TypeVar, overload

_T = TypeVar("_T")
_R_co = TypeVar("_R_co", covariant=True)


@overload
async def run_always_await(callable: Callable[..., _T], *args, **kwargs) -> _T:
    ...


@overload
async def run_always_await(callable: Callable[..., Awaitable[_T]], *args, **kwargs) -> _T:
    ...


@overload
async def run_always_await(callable: Callable[..., Coroutine[None, None, _T]], *args, **kwargs) -> _T:
    ...


async def run_always_await(callable, *args, **kwargs):
    obj = callable(*args, **kwargs)
    while isawaitable(obj):
        obj = await obj
    return obj


def identity(obj: Any) -> str:
    return obj.__name__ if isinstance(obj, type) else obj.__class__.__name__


class classproperty(Generic[_R_co]):
    fget: classmethod[_R_co]

    def __init__(self, fget: Callable[[Any], _R_co] | classmethod[_R_co]) -> None:
        if not isinstance(fget, classmethod):
            fget = classmethod(fget)

        self.fget = fget

    def __get__(self, __obj: _T, __type: type[_T] | None = None, /) -> _R_co:
        return self.fget.__get__(__obj, __type)()
