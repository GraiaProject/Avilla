from __future__ import annotations

from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from .perform import BasePerform
    from .typing import P, R, SupportsCollect

T = TypeVar("T")


class BaseCollector:
    artifacts: dict[Any, Any]
    collected_callbacks: list[Callable[[type[BasePerform]], Any]]

    def __init__(self) -> None:
        self.artifacts = {}
        self.collected_callbacks = [self.__post_collected__]

    def __post_collected__(self, cls: type[BasePerform]):
        self.cls = cls

    def _(self):
        class LocalPerformTemplate(BasePerform, native=True):
            __collector__ = self

        return LocalPerformTemplate

    def collect(self, signature: Any, artifact: Any):
        self.artifacts[signature] = artifact

    def on_collected(self, func: Callable[[type], Any]):
        self.collected_callbacks.append(func)

    def using(self, context_manager: AbstractContextManager[T]) -> T:
        self.on_collected(lambda _: context_manager.__exit__(None, None, None))
        return context_manager.__enter__()

    def post_merge(self, origin: dict):
        self.on_collected(lambda _: origin.update(self.artifacts))

    def entity(self, signature: SupportsCollect[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return signature.collect(self, *args, **kwargs)
