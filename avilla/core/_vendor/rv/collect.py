from __future__ import annotations

from .protocol import SupportsCollect

from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Callable, Any, TypeVar
from typing_extensions import ParamSpec, Self

if TYPE_CHECKING:
    from .isolate import Isolate


P = ParamSpec("P")
R = TypeVar("R", covariant=True)
T = TypeVar("T")

class Collector:
    artifacts: dict[Any, Any]
    ring3_callbacks: list[Callable[[type], Any]]

    def __init__(self):
        self.artifacts = {}
        self.ring3_callbacks = []

    def entity(self, signature: SupportsCollect[Self, P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return signature.collect(self, *args, **kwargs)

    def _base_ring3(self):
        class collect_ring3:
            __collector__ = self

            def __init_subclass__(cls) -> None:
                for i in self.ring3_callbacks:
                    i(cls)

        return collect_ring3

    def defer(self, func: Callable[[type], Any]):
        self.ring3_callbacks.append(func)

    def x(self, context_manager: AbstractContextManager[T]) -> T:
        self.defer(lambda _: context_manager.__exit__(None, None, None))
        return context_manager.__enter__()

    def apply(self, isolate: Isolate):
        self.defer(lambda x: isolate.apply(x))