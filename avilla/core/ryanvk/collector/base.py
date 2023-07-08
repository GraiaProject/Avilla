from __future__ import annotations

from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Protocol, TypeVar

from typing_extensions import ParamSpec, Self

from ..protocol import SupportsCollect

if TYPE_CHECKING:
    from ..isolate import Isolate
    from ..protocol import Ring3
    from ..runner import Runner


P = ParamSpec("P")
R = TypeVar("R", covariant=True)
T = TypeVar("T")


class PerformTemplate:
    __collector__: ClassVar[BaseCollector]
    runner: Runner

    def __init__(self, runner: Runner):
        self.runner = runner


class _ResultCollect(Protocol[R]):
    @property
    def _(self) -> R:
        ...


class BaseCollector:
    artifacts: dict[Any, Any]
    defer_callbacks: list[Callable[[type[Ring3]], Any]]

    @property
    def cls(self: _ResultCollect[R]) -> R:
        if TYPE_CHECKING:
            return self._
        return self._cls

    @property
    def _(self):
        return self.get_collect_template()

    def __init__(self):
        self.artifacts = {}
        self.defer_callbacks = [self.__post_collect__]

    def entity(self, signature: SupportsCollect[Self, P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return signature.collect(self, *args, **kwargs)

    def get_collect_template(self):
        class LocalPerformTemplate(PerformTemplate):
            __collector__ = self

            def __init_subclass__(cls) -> None:
                if getattr(cls, "__native__", False):
                    delattr(cls, "__native__")
                    return

                for i in self.defer_callbacks:
                    i(cls)

        return LocalPerformTemplate

    def defer(self, func: Callable[[type], Any]):
        self.defer_callbacks.append(func)

    def x(self, context_manager: AbstractContextManager[T]) -> T:
        self.defer(lambda _: context_manager.__exit__(None, None, None))
        return context_manager.__enter__()

    def apply(self, isolate: Isolate):
        self.defer(lambda x: isolate.apply(x))

    def __post_collect__(self, cls: type[Ring3]):
        self._cls = cls
