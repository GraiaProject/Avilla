from __future__ import annotations

from collections import ChainMap
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol

from typing_extensions import Concatenate, ParamSpec, TypeVar

from ..collector.base import BaseCollector

if TYPE_CHECKING:
    from ..capability import Capability
    from ..collector.base import PerformTemplate


class _Callable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R", covariant=True)
VnCallable = TypeVar("VnCallable", bound="_Callable", covariant=True)
HQ = TypeVar("HQ", bound="PerformTemplate", contravariant=True)


@dataclass(unsafe_hash=True)
class FnImplement:
    capability: type[Capability]
    name: str


class Fn(Generic[VnCallable]):
    capability: type[Capability]
    name: str = "<unit>"
    template: Callable

    def __init__(self: Fn[Callable[P, R]], template: Callable[Concatenate[Any, P], R]):
        self.template = template

    def __set_name__(self, owner: type[Capability], name: str):
        self.capability = owner
        self.name = name

    def collect(
        self: Fn[Callable[P, R]],  # pyright: ignore[reportInvalidTypeVarUse]
        collector: BaseCollector,
        signature: Any,
    ):
        def wrapper(entity: Callable[Concatenate[HQ, P], R]):
            collector.artifacts[signature] = (collector, entity)
            return entity

        return wrapper

    def get_artifact_record(
        self: Fn[Callable[P, Any]],
        collection: ChainMap[Any, Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> tuple[BaseCollector, Callable[Concatenate[Any, P], Any]]:
        return collection[FnImplement(self.capability, self.name)]
