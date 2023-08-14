from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Protocol

from typing_extensions import Concatenate, ParamSpec, TypeVar

if TYPE_CHECKING:
    from .collector import BaseCollector  # noqa

P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", infer_variance=True)
T = TypeVar("T")
C = TypeVar("C", bound="BaseCollector")
CD = TypeVar("CD", default="BaseCollector", infer_variance=True)


class SupportsCollect(Protocol[P, R, CD]):
    def collect(self: SupportsCollect[P, R, CD], collector: CD, *args: P.args, **kwargs: P.kwargs) -> R:
        ...


class OutboundCompatible(Protocol[P, T, P1]):
    def get_artifact_record(
        self,
        collections: list[dict[Any, Any]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[Any, Callable[Concatenate[Any, P], T]]:
        ...

    def get_outbound_callable(self, instance: Any, entity: Callable[Concatenate[Any, P], T]) -> Callable[P1, T]:
        ...
