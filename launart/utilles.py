from __future__ import annotations

import asyncio
import enum
from typing import (
    TYPE_CHECKING,
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

from loguru import logger

if TYPE_CHECKING:
    from launart.component import Launchable

T = TypeVar("T")
H = TypeVar("H", bound=Hashable)

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


class _Unmarked(enum.Enum):
    UNMARKED = object()


UNMARKED = _Unmarked.UNMARKED
# "Unmarked" is a great way of replacing ellipsis.


class RequirementResolveFailed(ValueError):
    pass


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
                    return

    def add(self, *fs: asyncio.Task | Coroutine) -> None:
        tasks = [f if isinstance(f, asyncio.Task) else asyncio.create_task(f) for f in fs]
        if self.blocking_task is not None:
            self.blocking_task.cancel()
        self.tasks.extend(tasks)


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


async def any_completed(*waits):
    return await asyncio.wait(
        [i if isinstance(i, asyncio.Task) else asyncio.create_task(i) for i in waits],
        return_when=asyncio.FIRST_COMPLETED,
    )


def cancel_alive_tasks(loop: asyncio.AbstractEventLoop):
    to_cancel = asyncio.tasks.all_tasks(loop)
    if to_cancel:
        for tsk in to_cancel:
            print(tsk)
            tsk.cancel()
        loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))

        for task in to_cancel:  # pragma: no cover
            # BELIEVE IN PSF
            if task.cancelled():
                continue
            if task.exception() is not None:
                logger.opt(exception=task.exception()).error(f"Unhandled exception when shutting down {task}:")


def resolve_requirements(components: Iterable[Launchable], reverse: bool = False) -> List[Set[Launchable]]:
    resolved_id: Set[str] = set()
    unresolved: Set[Launchable] = set(components)
    result: List[Set[Launchable]] = []
    while unresolved:
        layer = {component for component in unresolved if resolved_id >= component.required}

        if layer:
            unresolved -= layer
            resolved_id.update(component.id for component in layer)
            result.append(layer)
        else:
            raise RequirementResolveFailed(unresolved)
    if reverse:
        result.reverse()
    return result
