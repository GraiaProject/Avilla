import inspect
from typing import Awaitable, Callable, Coroutine, TypeVar, overload

T = TypeVar("T")


@overload
async def run_always_await(callable: Callable[..., T], *args, **kwargs) -> T:
    ...

@overload
async def run_always_await(callable: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    ...

@overload
async def run_always_await(callable: Callable[..., Coroutine[None, None, T]], *args, **kwargs) -> T:
    ...

async def run_always_await(callable, *args, **kwargs):
    obj = callable(*args, **kwargs)
    while inspect.isawaitable(obj):
        obj = await obj
    return obj
