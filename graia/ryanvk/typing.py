from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from .collector import BaseCollector

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class SupportsCollect(Protocol[P, R]):
    def collect(self, collector: BaseCollector, *args: P.args, **kwargs: P.kwargs) -> R:
        ...
