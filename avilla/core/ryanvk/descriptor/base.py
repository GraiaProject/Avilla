from __future__ import annotations

from collections import ChainMap
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, overload

from typing_extensions import Concatenate, ParamSpec, Self, TypeVar

if TYPE_CHECKING:
    from avilla.core.ryanvk.capability import Capability
    from avilla.core.ryanvk.collector.base import BaseCollector, PerformTemplate
    from avilla.core.ryanvk.protocol import SupportsCollect


class _Callable(Protocol):
    __call__: Callable


T = TypeVar("T")
P = ParamSpec("P")
P1 = ParamSpec("P1")
R = TypeVar("R", covariant=True)
Q = TypeVar("Q", contravariant=True)
VnCallable = TypeVar("VnCallable", bound="_Callable", covariant=True)
HQ = TypeVar("HQ", bound="PerformTemplate", contravariant=True)
WrapperCallable = Callable[[Q], Q]


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

    def override(
        self: SupportsCollect[Any, P1, WrapperCallable[Callable[Concatenate[Any, P], R]]],  # pyright: ignore
        collector: BaseCollector,
        *args: P1.args,
        **kwargs: P1.kwargs,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P], R]) -> OverridePerformEntity[P, R]:
            self.collect(collector, *args, **kwargs)(entity)
            return OverridePerformEntity(collector, self, entity)  # type: ignore

        return wrapper


class OverridePerformEntity(Generic[P, R]):
    collector: BaseCollector
    fn: Fn[Callable[P, R]]
    entity: Callable[Concatenate[Any, P], R]

    origin_perform: type[PerformTemplate]
    name: str

    def __init__(
        self,
        collector: BaseCollector,
        fn: Fn[Callable[P, R]],
        entity: Callable[Concatenate[Any, P], R],
    ) -> None:
        self.collector = collector
        self.fn = fn
        self.entity = entity

    @classmethod
    def collect(
        cls,
        collector: BaseCollector,
        fn: SupportsCollect[Any, P1, WrapperCallable[Callable[Concatenate[Any, P], R]]],
        *args: P1.args,
        **kwargs: P1.kwargs,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P], R]) -> OverridePerformEntity[P, R]:
            fn.collect(collector, *args, **kwargs)(entity)
            return cls(collector, fn, entity)  # type: ignore

        return wrapper

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
    def __get__(self, instance: PerformTemplate, owner: type[PerformTemplate]) -> OverridePerformAgent[P, R]:
        ...

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self

        return OverridePerformAgent(self, instance)


class OverridePerformAgent(Generic[P, R]):
    perform_entity: OverridePerformEntity[P, R]
    instance: PerformTemplate

    def __init__(self, perform_entity: OverridePerformEntity[P, R], instance: PerformTemplate) -> None:
        self.perform_entity = perform_entity
        self.instance = instance

    def __call__(self, *args: P.args, **kwds: P.kwargs) -> R:
        return self.perform_entity.entity(self.instance, *args, **kwds)

    def super(self, *args: P.args, **kwds: P.kwargs) -> R:
        return self.instance.dispatched_overrides[(type(self.instance), self.perform_entity.name)](
            self.instance, *args, **kwds
        )
