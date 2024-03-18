from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Callable, Container, Protocol, overload

from avilla.core.selector import Selector, _FollowItem
from graia.ryanvk import BaseCollector


@dataclass(unsafe_hash=True)
class QueryRecord:
    """仅用作计算路径, 不参与实际运算, 也因此, 该元素仅存在于全局 Artifacts['query'] 中."""

    previous: str | None
    into: str


class QueryHandlerPerform(Protocol):
    def __call__(
        fself, self: Any, predicate: Callable[[str, str], bool] | str, previous: Selector | None = None
    ) -> AsyncGenerator[Selector, None]:
        ...


class QueryHandlerPerformNoPrev(Protocol):
    def __call__(
        fself, self: Any, predicate: Callable[[str, str], bool] | str, previous: None
    ) -> AsyncGenerator[Selector, None]:
        ...


class QueryHandlerPerformPrev(Protocol):
    def __call__(
        fself, self: Any, predicate: Callable[[str, str], bool] | str, previous: Selector
    ) -> AsyncGenerator[Selector, None]:
        ...


class QuerySchema:
    @overload
    def collect(
        self, collector: BaseCollector, target: str, previous: None = None
    ) -> Callable[[QueryHandlerPerformNoPrev], QueryHandlerPerformNoPrev]:
        ...

    @overload
    def collect(
        self, collector: BaseCollector, target: str, previous: str
    ) -> Callable[[QueryHandlerPerformPrev], QueryHandlerPerformPrev]:
        ...

    def collect(self, collector: BaseCollector, target: str, previous: ... = None) -> ...:
        def receive(entity: QueryHandlerPerform):
            collector.artifacts[QueryRecord(previous, target)] = (collector, entity)
            return entity

        return receive


class QueryHandler(Protocol):
    def __call__(
        self, predicate: Callable[[str, str], bool] | str, previous: Selector | None = None
    ) -> AsyncGenerator[Selector, None]:
        ...


# 使用 functools.reduce.
async def query_depth_generator(
    handler: QueryHandler,
    predicate: Callable[[str, str], bool] | str,
    previous_generator: AsyncGenerator[Selector, None] | None = None,
):
    if previous_generator is not None:
        async for previous in previous_generator:
            async for current in handler(predicate, previous):
                yield current
    else:
        async for current in handler(predicate):
            yield current


@dataclass
class _MatchStep:
    upper: str
    start: int
    history: tuple[tuple[tuple[_FollowItem, ...], QueryRecord], ...]


def find_querier_steps(
    artifacts: Container[Any],
    frags: list[_FollowItem],
) -> list[tuple[tuple[_FollowItem, ...], QueryRecord]] | None:
    result: list[tuple[tuple[_FollowItem, ...], QueryRecord]] | None = None
    queue: deque[_MatchStep] = deque([_MatchStep("", 0, ())])
    whole = ".".join([i.name for i in frags])
    while queue:
        head: _MatchStep = queue.popleft()
        current_steps: list[_FollowItem] = []
        for curr_frag in frags[head.start :]:
            current_steps.append(curr_frag)
            steps = ".".join([i.name for i in current_steps])
            full_path = f"{head.upper}.{steps}" if head.upper else steps
            head.start += 1
            if (query := ((*current_steps,), QueryRecord(head.upper or None, steps)))[1] in artifacts:
                if full_path == whole:
                    if result is None or len(result) > len(head.history) + 1:
                        result = [*head.history, query]
                else:
                    queue.append(_MatchStep(full_path, head.start, head.history + (query,)))
    return result
