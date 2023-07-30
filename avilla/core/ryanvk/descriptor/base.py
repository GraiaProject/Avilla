from __future__ import annotations

from collections import ChainMap
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, overload

from typing_extensions import Concatenate, ParamSpec, Self, TypeVar

from avilla.core.ryanvk.collector.base import BaseCollector

if TYPE_CHECKING:
    from avilla.core.ryanvk.capability import Capability
    from avilla.core.ryanvk.collector.base import PerformTemplate


class _Callable(Protocol):
    __call__: Callable


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

    def get_outbound_callable(self: Fn[Callable[P, R]], instance: Any, entity: Callable[Concatenate[Any, P], R]):
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return entity(instance, *args, **kwargs)

        return wrapper


class OverridePerformEntity(Generic[VnCallable]):
    collector: BaseCollector
    fn: Fn[VnCallable]
    entity: VnCallable

    origin_perform: type[PerformTemplate]
    name: str

    def __init__(self, collector: BaseCollector, fn: Fn[VnCallable], entity: VnCallable) -> None:
        self.collector = collector
        self.fn = fn
        self.entity = entity
    
    def __set_name__(self, owner: type[PerformTemplate], name: str):
        self.origin_perform = owner
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type[PerformTemplate]) -> Self:
        ...

    @overload
    def __get__(self, instance: OverridePerformAgent, owner: type) -> Self:
        ...

    @overload
    def __get__(self, instance: PerformTemplate, owner: type[PerformTemplate]) -> OverridePerformAgent[VnCallable]:
        ...
    
    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self
    
        return OverridePerformAgent(self, instance)

class OverridePerformAgent(Generic[VnCallable]):
    perform_entity: OverridePerformEntity[VnCallable]
    instance: PerformTemplate

    def __init__(self, perform_entity: OverridePerformEntity[VnCallable], instance: PerformTemplate) -> None:
        self.perform_entity = perform_entity
        self.instance = instance
    
    def __call__(self: OverridePerformAgent[Callable[P, R]], *args: P.args, **kwds: P.kwargs) -> R:
        return self.perform_entity.entity(*args, **kwds)
    
    def super(self: OverridePerformAgent[Callable[P, R]], *args: P.args, **kwds: P.kwargs) -> R:
        # 这里还存有疑问。
        return self.instance.dispatched_override[(type(self.instance), self.perform_entity.name)](*args, **kwds)
