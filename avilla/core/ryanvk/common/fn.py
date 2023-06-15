from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, TypeVar

from typing_extensions import ParamSpec

from avilla.core._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from .capability import Capability
    from .collect import BaseCollector
    from .runner import Runner

P = ParamSpec("P")
T = TypeVar("T", covariant=True)


@dataclass(unsafe_hash=True)
class FnImplement:
    capability: type[Capability]
    name: str


class BaseFn(Generic[P, T]):
    capability: type[Capability]
    name: str = "<unit>"
    template: Callable[P, T]

    def __set_name__(self, owner: type[Capability], name: str):
        self.capability = owner
        self.name = name

    def signature_on_collect(self):
        return FnImplement(self.capability, self.name)

    def collect(self, collector: BaseCollector):
        def wrapper(entity: Callable[P, T]):
            collector.artifacts[self.signature_on_collect()] = entity
            return entity

        return wrapper

    def execute(self, runner: Runner, *args: P.args, **kwargs: P.kwargs) -> T:
        return runner.artifacts[self.signature_on_collect()](*args, **kwargs)
