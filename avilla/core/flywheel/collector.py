from __future__ import annotations

from typing import Any, Callable, MutableMapping, TypeVar

from typing_extensions import Self

from .perform import BasePerform
from .typing import P, R, SupportsCollect

T = TypeVar("T")


class BaseCollector:
    artifacts: MutableMapping[Any, Any]
    collected_callbacks: list[Callable[[type[BasePerform]], Any]]

    def __init__(self, artifacts: dict[Any, Any] | None = None) -> None:
        self.artifacts = artifacts or {}
        self.collected_callbacks = [self.__post_collected__]

    def __post_collected__(self, cls: type[BasePerform]):
        self.cls = cls

    @property
    def _(self):
        class LocalPerformTemplate(BasePerform, keep_native=True):
            __collector__ = self

        return LocalPerformTemplate

    def on_collected(self, func: Callable[[type], Any]):
        self.collected_callbacks.append(func)

    def remove_collected_callback(self, func: Callable[[type], Any]):
        self.collected_callbacks.remove(func)

    def collect(
        self,
        signature: SupportsCollect[Self, P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        return signature.collect(self, *args, **kwargs)
