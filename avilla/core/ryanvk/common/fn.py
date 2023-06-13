from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from .capability import Capability
    from .collect import BaseCollector
    from .runner import Runner

P = ParamSpec("P")
T = TypeVar("T", covariant=True)


@dataclass
class FnImplement:
    fn: BaseFn


class BaseFn(Generic[P, T]):
    capability: type[Capability] | None = None
    name: str = "<unit>"
    template: Callable[P, T]

    def __set_name__(self, owner: type[Capability], name: str):
        self.capability = owner
        self.name = name

    @property
    def signature(self):
        return FnImplement(self)

    def collect(self, collector: BaseCollector):
        def wrapper(entity: Callable[P, T]):
            collector.artifacts[self.signature] = entity
            return entity

        return wrapper

    def execute(self, runner: Runner, *args: P.args, **kwargs: P.kwargs) -> T:
        return runner.artifacts[self.signature](*args, **kwargs)
