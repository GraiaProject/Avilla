from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec, Self

if TYPE_CHECKING:
    from .collector import BaseCollector
    from .fn import Fn
    from .perform import BasePerform
    from .typing import SupportsCollect

P = ParamSpec("P")
R = TypeVar("R", covariant=True)
P1 = ParamSpec("P1")
Q = TypeVar("Q", contravariant=True)

WrapperCallable = Callable[[Q], Q]
FnRecord = tuple["BaseCollector", Callable]


class OverridePerformEntity(Generic[P, R]):
    collector: BaseCollector
    fn: Fn[P, R]
    entity: Callable[Concatenate[Any, P], R]

    origin_perform: type[BasePerform]
    name: str

    def __init__(
        self,
        collector: BaseCollector,
        fn: Fn[P, R],
        entity: Callable[Concatenate[Any, P], R],
    ) -> None:
        self.collector = collector
        self.fn = fn
        self.entity = entity

    @classmethod
    def collect(
        cls,
        collector: BaseCollector,
        fn: SupportsCollect[P1, WrapperCallable[Callable[Concatenate[Any, P], R]]],
        *args: P1.args,
        **kwargs: P1.kwargs,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P], R]) -> OverridePerformEntity[P, R]:
            fn.collect(collector, *args, **kwargs)(entity)
            return cls(collector, fn, entity)  # type: ignore

        return wrapper

    def __set_name__(self, owner: type[BasePerform], name: str):
        self.origin_perform = owner
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type[BasePerform]) -> Self:
        ...

    @overload
    def __get__(self, instance: OverridePerformAgent, owner: type) -> Self:
        ...

    @overload
    def __get__(self, instance: BasePerform, owner: type[BasePerform]) -> OverridePerformAgent[P, R]:
        ...

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self

        return OverridePerformAgent(self, instance)


class OverridePerformAgent(Generic[P, R]):
    perform_entity: OverridePerformEntity[P, R]
    instance: BasePerform

    def __init__(self, perform_entity: OverridePerformEntity[P, R], instance: BasePerform) -> None:
        self.perform_entity = perform_entity
        self.instance = instance

    def __call__(self, *args: P.args, **kwds: P.kwargs) -> R:
        return self.perform_entity.entity(self.instance, *args, **kwds)

    def super(self, *args: P.args, **kwds: P.kwargs) -> R:
        origin = self.instance.staff
        collections = origin.artifact_collections[1:]
        staff_type = type(origin)
        staff = staff_type(collections, origin.components)
        staff.instances.update(origin.instances)
        staff.exit_stack = origin.exit_stack
        return staff.call_fn(self.perform_entity.fn, *args, **kwds)
