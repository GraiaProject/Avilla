from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, NoReturn, TypeVar

from typing_extensions import Concatenate, ParamSpec

from avilla.core._vendor.dataclasses import dataclass

if TYPE_CHECKING:
    from .capability import Capability
    from .collect import BaseCollector
    from .runner import Runner

P = ParamSpec("P")
T = TypeVar("T", covariant=True)
C = TypeVar("C", contravariant=True, bound="BaseCollector")
X = TypeVar("X", bound=NoReturn, contravariant=True)


@dataclass(unsafe_hash=True)
class FnImplement:
    capability: type[Capability]
    name: str


class BaseFn(Generic[C, P, T]):
    capability: type[Capability]
    name: str = "<unit>"
    template: Callable[P, T]

    def __set_name__(self, owner: type[Capability], name: str):
        self.capability = owner
        self.name = name

    def collect(self, collector: C):
        def wrapper(entity: Callable[Concatenate[X, P], T]):
            collector.artifacts[FnImplement(self.capability, self.name)] = entity
            return entity

        return wrapper

    def execute(self, runner: Runner, *args: P.args, **kwargs: P.kwargs) -> T:
        return runner.artifacts[FnImplement(self.capability, self.name)](*args, **kwargs)
