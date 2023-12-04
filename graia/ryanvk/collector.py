from __future__ import annotations

from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Any, Callable, MutableMapping, TypeVar

from ._runtime import targets_artifact_map
from .perform import BasePerform

if TYPE_CHECKING:
    from .typing import P, R, SupportsCollect

T = TypeVar("T")


class BaseCollector:
    artifacts: MutableMapping[Any, Any]
    collected_callbacks: list[Callable[[type[BasePerform]], Any]]

    _upstream_target: bool = False

    @property
    def upstream_target(self):
        return self._upstream_target

    @upstream_target.setter
    def _upstream_target_setter(self, value: bool):
        self._upstream_target = value

        if value:
            self.artifacts = targets_artifact_map.get(None) or {}

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

    def using(self, context_manager: AbstractContextManager[T]) -> T:
        self.on_collected(lambda _: context_manager.__exit__(None, None, None))
        return context_manager.__enter__()

    def entity(
        self,
        signature: SupportsCollect[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        return signature.collect(self, *args, **kwargs)
