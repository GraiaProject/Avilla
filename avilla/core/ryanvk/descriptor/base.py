from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol

from typing_extensions import Concatenate, ParamSpec, TypeVar

from ..collector.base import BaseCollector
from ..runner import Runner

if TYPE_CHECKING:
    from ..capability import Capability
    from ..collector.base import PerformTemplate


class _Callable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R", covariant=True)
VnCallable = TypeVar("VnCallable", bound="_Callable")
VnCollector = TypeVar("VnCollector", bound="BaseCollector", default="BaseCollector")
VnRunner = TypeVar("VnRunner", bound="Runner", default="Runner")
HQ = TypeVar("HQ", bound="PerformTemplate", contravariant=True)


@dataclass(unsafe_hash=True)
class FnImplement:
    capability: type[Capability]
    name: str


class Fn(Generic[VnCallable, VnCollector, VnRunner]):
    capability: type[Capability]
    name: str = "<unit>"
    template: Callable

    def __init__(self: Fn[Callable[P, R], VnCollector, VnRunner], template: Callable[Concatenate[Any, P], R]):
        self.template = template

    def __set_name__(self, owner: type[Capability], name: str):
        self.capability = owner
        self.name = name

    def collect(
        self: Fn[Callable[P, R], VnCollector, VnRunner],  # pyright: ignore[reportInvalidTypeVarUse]
        collector: VnCollector,
        signature: Any,
    ):
        def wrapper(entity: Callable[Concatenate[HQ, P], R]):
            collector.artifacts[signature] = (collector, entity)
            return entity

        return wrapper

    def get_artifact_record(
        self: Fn[Callable[P, Any], VnCollector, VnRunner],
        runner: VnRunner,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[VnCollector, Callable[Concatenate[Any, P], Any]]:
        return runner.artifacts[FnImplement(self.capability, self.name)]

    def execute(
        self: Fn[Callable[P, R], VnCollector, VnRunner],
        runner: VnRunner,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        collector, entity = self.get_artifact_record(runner, *args, **kwargs)
        instance = collector.cls(runner)
        return entity(instance, *args, **kwargs)
