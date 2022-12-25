from __future__ import annotations

from collections import deque
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.amnesia.message import __message_chain_class__
from typing_extensions import TypeAlias

from avilla.core.selector import Selector
from avilla.core.trait.context import Artifacts
from avilla.core.trait.signature import Query

if TYPE_CHECKING:
    from . import Context

_Querier: TypeAlias = Callable[["Context", Selector | None, Selector], AsyncGenerator[Selector, None]]


async def query_depth_generator(
    context: Context,
    current: _Querier,
    predicate: Selector,
    upper_generator: AsyncGenerator[Selector, None] | None = None,
):
    if upper_generator is not None:
        async for i in upper_generator:
            async for j in current(context, i, predicate):
                yield j
    else:
        async for j in current(context, None, predicate):
            yield j


@dataclass
class _MatchStep:
    upper: str
    start: int
    history: tuple[Query, ...]


def find_querier_steps(artifacts: Artifacts, query_path: str) -> list[Query] | None:
    result: list[Query] | None = None
    frags: list[str] = query_path.split(".")
    queue: deque[_MatchStep] = deque([_MatchStep("", 0, ())])
    while queue:
        head: _MatchStep = queue.popleft()
        current_steps: list[str] = []
        for curr_frag in frags[head.start :]:
            current_steps.append(curr_frag)
            steps = ".".join(current_steps)
            full_path = f"{head.upper}.{steps}" if head.upper else steps
            head.start += 1
            if (query := Query(head.upper or None, steps)) in artifacts:
                if full_path == query_path:
                    if result is None or len(result) > len(head.history) + 1:
                        result = [*head.history, query]
                else:
                    queue.append(
                        _MatchStep(
                            full_path,
                            head.start,
                            head.history + (query,),
                        )
                    )
    return result
