from __future__ import annotations

import asyncio
import enum
from typing import (
    Callable,
    Coroutine,
    Dict,
    Hashable,
    Iterable,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

T = TypeVar("T")
H = TypeVar("H", bound=Hashable)


class _Unmarked(enum.Enum):
    UNMARKED = object()


UNMARKED = _Unmarked.UNMARKED

# "Unmarked" is a great way of replacing ellipsis.

PriorityType = Union[
    Set[T],
    Dict[T, float],
    Tuple[
        Union[
            Set[T],
            Dict[T, float],
        ],
        ...,
    ],
]


def priority_strategy(
    items: List[T],
    getter: Callable[
        [T],
        PriorityType[H],
    ],
) -> Dict[H, T]:
    result: Dict[H, T] = {}
    _priority_mem: Dict[H, float | Literal[UNMARKED]] = {}

    def _handle(pattern: PriorityType[H]) -> None:
        """Handle an actual pattern."""
        if isinstance(pattern, set):
            # Pattern has unknown priorities.
            for content in pattern:
                if content in _priority_mem:
                    raise ValueError(f"{content} conflicts with {result[content]}")
                _priority_mem[content] = UNMARKED
                result[content] = item

        elif isinstance(pattern, dict):
            for content, priority in pattern.items():
                if content in _priority_mem:
                    current_priority: float | Literal[_Unmarked.UNMARKED] = _priority_mem[content]
                    if current_priority is UNMARKED or priority is UNMARKED:
                        raise ValueError(f"Unable to determine priority order: {content}, {result[content]}.")
                    if current_priority < priority:
                        _priority_mem[content] = priority
                        result[content] = item
                else:
                    _priority_mem[content] = priority
                    result[content] = item

        else:
            raise TypeError(f"{pattern} is not a valid pattern.")

    for item in items:
        pattern: PriorityType[H] = getter(item)
        if isinstance(pattern, (dict, set)):
            _handle(pattern)
        elif isinstance(pattern, tuple):
            for sub_pattern in pattern:
                _handle(sub_pattern)
        else:
            raise TypeError(f"{pattern} is not a valid pattern.")
    return result


async def wait_fut(
    coros: Iterable[Union[Coroutine, asyncio.Task]],
    *,
    timeout: Optional[float] = None,
    return_when: str = asyncio.ALL_COMPLETED,
) -> None:
    tasks = []
    for c in coros:
        if asyncio.iscoroutine(c):
            tasks.append(asyncio.create_task(c))
        else:
            tasks.append(c)
    if tasks:
        await asyncio.wait(tasks, timeout=timeout, return_when=return_when)


class FlexibleTaskGroup:
    tasks: list[asyncio.Task]
    sideload_trackers: dict[str, asyncio.Task]
    blocking_task: Optional[asyncio.Task] = None
    stop: bool = False

    def __init__(self, *tasks):
        self.sideload_trackers = {}
        self.tasks = list(tasks)

    def __await__(self):
        return self.__await_impl__().__await__()

    async def __await_impl__(self):
        while True:
            self.blocking_task = asyncio.create_task(asyncio.wait(self.tasks))
            try:
                return await self.blocking_task
            except asyncio.CancelledError:
                if self.stop:
                    raise

    def add(self, *fs: asyncio.Task | Coroutine) -> None:
        tasks = [f if isinstance(f, asyncio.Task) else asyncio.create_task(f) for f in fs]
        if self.blocking_task is not None:
            self.blocking_task.cancel()
        self.tasks.extend(tasks)
