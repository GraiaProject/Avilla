from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator, Callable, Protocol
from typing import NoReturn as Never

from ..._vendor.dataclasses import dataclass
from ...selector import Selector

if TYPE_CHECKING:
    from ..collector.context import ContextCollector


@dataclass
class QueryRecord:
    """仅用作计算路径, 不参与实际运算, 也因此, 该元素仅存在于全局 Artifacts['query'] 中."""

    previous: str | None
    into: str


class QueryHandlerPerform(Protocol):
    def __call__(
        self, _p0: Never, predicate: Callable[[str, str], bool] | str, previous: Selector | None = None
    ) -> AsyncGenerator[Selector, None]:
        ...


class QuerySchema:
    def collect(self, collector: ContextCollector, target: str, previous: str | None = None):
        def receive(entity: QueryHandlerPerform):
            collector.artifacts[QueryRecord(previous, target)] = (collector, entity)
            return entity

        return receive
