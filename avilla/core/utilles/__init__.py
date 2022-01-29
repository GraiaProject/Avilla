import asyncio
import random
import string
from contextlib import suppress
from types import TracebackType
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from graia.broadcast import BaseDispatcher, DispatcherInterface
from graia.broadcast.utilles import run_always_await_safely


def random_string(k: int = 12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))


def as_async(func):
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


T = TypeVar("T")
H = TypeVar("H", bound=Hashable)


def priority_strategy(
    items: List[T],
    getter: Callable[
        [T], Union[Set[H], Dict[H, Union[int, float]], Tuple[Union[Set[H], Dict[H, Union[int, float]]], ...]]
    ],
) -> Dict[H, T]:
    result = {}
    priorities_cache = {}
    for item in items:
        pattern = getter(item)
        if isinstance(pattern, Set):
            for content in pattern:
                if content in priorities_cache:
                    raise ValueError(
                        f"{content} which is an unlocated item is already existed, and it conflicts with {result[content]}"
                    )
                priorities_cache[content] = ...
                result[content] = item
        elif isinstance(pattern, Dict):
            for content, priority in pattern.items():
                if content in priorities_cache:
                    if priorities_cache[content] is ...:
                        raise ValueError(
                            f"{content} is already existed, and it conflicts with {result[content]}, an unlocated item."
                        )
                    if priority is ...:
                        raise ValueError(
                            f"{content} which is an unlocated item is already existed, and it conflicts with {result[content]}"
                        )
                    if priorities_cache[content] < priority:
                        priorities_cache[content] = priority
                        result[content] = item
                else:
                    priorities_cache[content] = priority
                    result[content] = item
        elif isinstance(pattern, Tuple):
            for subpattern in pattern:
                if isinstance(subpattern, Set):
                    for content in subpattern:
                        if content in priorities_cache:
                            raise ValueError(
                                f"{content} which is an unlocated item is already existed, and it conflicts with {result[content]}"
                            )
                        priorities_cache[content] = ...
                        result[content] = item
                elif isinstance(subpattern, Dict):
                    for content, priority in subpattern.items():
                        if content in priorities_cache:
                            if priorities_cache[content] is ...:
                                raise ValueError(
                                    f"{content} is already existed, and it conflicts with {result[content]}, an unlocated item."
                                )
                            if priority is ...:
                                raise ValueError(
                                    f"{content} which is an unlocated item is already existed, and it conflicts with {result[content]}"
                                )
                            if priorities_cache[content] < priority:
                                priorities_cache[content] = priority
                                result[content] = item
                        else:
                            priorities_cache[content] = priority
                            result[content] = item
                else:
                    raise TypeError(f"{subpattern} is not a valid pattern.")
        else:
            raise TypeError(f"{pattern} is not a valid pattern.")
    return result


class Defer:
    def __init__(self, defers: List[Callable[[], Any]]) -> None:
        self.defers = defers

    def add(self, defer: Callable[[], Any]) -> None:
        self.defers.append(defer)


class DeferDispatcher(BaseDispatcher):
    async def beforeExecution(self, interface: DispatcherInterface):
        interface.local_storage["defers"] = []

    async def catch(self, interface: DispatcherInterface):
        if interface.annotation is Defer:
            return Defer(interface.local_storage["defers"])

    async def afterExecution(
        self, interface: DispatcherInterface, exception: Optional[Exception], tb: Optional[TracebackType]
    ):
        await asyncio.gather(*[run_always_await_safely(defer) for defer in interface.local_storage["defers"]])
