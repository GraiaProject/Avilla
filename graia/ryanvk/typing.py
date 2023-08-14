from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from typing_extensions import ParamSpec, TypeVar

if TYPE_CHECKING:
    from .collector import BaseCollector  # noqa

P = ParamSpec("P")
R = TypeVar("R", infer_variance=True)
C = TypeVar("C", default="BaseCollector", infer_variance=True)


class SupportsCollect(Protocol[P, R, C]):
    def collect(self: SupportsCollect[P, R, C], collector: C, *args: P.args, **kwargs: P.kwargs) -> R:
        ...
