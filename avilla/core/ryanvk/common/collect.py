from __future__ import annotations

from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Protocol, TypeVar

from typing_extensions import ParamSpec, Self

from .protocol import SupportsCollect

if TYPE_CHECKING:
    from .isolate import Isolate
    from .protocol import Ring3


P = ParamSpec("P")
R = TypeVar("R", covariant=True)
T = TypeVar("T")


class _ResultCollect(Protocol[R]):
    @property
    def _(self) -> R:
        ...


class BaseCollector:
    artifacts: dict[Any, Any]
    ring3_callbacks: list[Callable[[type[Ring3]], Any]]

    @property
    def cls(self: _ResultCollect[R]) -> R:
        if TYPE_CHECKING:
            return self._
        return self._cls

    def __init__(self):
        self.artifacts = {}
        self.ring3_callbacks = [self.__post_collect__]

    def entity(self, signature: SupportsCollect[Self, P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return signature.collect(self, *args, **kwargs)

    def _base_ring3(self):
        class collect_ring3:
            __collector__: ClassVar[BaseCollector] = self

            def __init_subclass__(cls) -> None:
                if getattr(cls, "__native__", False):
                    delattr(cls, "__native__")
                    return

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

    def __post_collect__(self, cls: type[Ring3]):
        self._cls = cls
