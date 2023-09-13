from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, Generic, overload

from typing_extensions import Concatenate, ParamSpec, Self, TypeVar

from .behavior import DEFAULT_BEHAVIOR, FnBehavior
from .override import OverridePerformEntity

if TYPE_CHECKING:
    from .capability import Capability
    from .collector import BaseCollector
    from .overload import FnOverload
    from .perform import BasePerform
    from .typing import SupportsCollect


P = ParamSpec("P")
P1 = ParamSpec("P1")
P2 = ParamSpec("P2")

R = TypeVar("R", covariant=True)
R1 = TypeVar("R1", covariant=True)
R2 = TypeVar("R2", covariant=True)

B = TypeVar("B", bound=FnBehavior, default=FnBehavior, covariant=True)


class Fn(Generic[P, R, B]):
    owner: type[BasePerform | Capability]  # TODO: review here
    name: str

    shape: Callable[Concatenate[Any, P], R]
    shape_signature: inspect.Signature

    behavior: B

    overload_params: dict[str, FnOverload]
    overload_param_map: dict[FnOverload, list[str]]
    overload_map: dict[str, FnOverload]

    def __init__(
        self,
        shape: Callable[Concatenate[Any, P], R],
        behavior: B = DEFAULT_BEHAVIOR,
        overload_param_map: dict[FnOverload, list[str]] | None = None,
    ):
        self.shape = shape
        self.shape_signature = inspect.Signature(list(inspect.Signature.from_callable(shape).parameters.values())[1:])
        self.behavior = behavior

        self.overload_param_map = overload_param_map or {}
        self.overload_params = {i: k for k, v in self.overload_param_map.items() for i in v}
        self.overload_map = {i.identity: i for i in self.overload_param_map}

    def __set_name__(self, owner: type[BasePerform], name: str):
        self.owner = owner
        self.name = name

    @overload
    def __get__(self, instance: BasePerform, owner: type) -> Callable[P, R]:
        ...

    @overload
    def __get__(self, instance: Any, owner: type) -> Self:
        ...

    def __get__(self, instance: BasePerform | None, owner: type):
        if not isinstance(instance, BasePerform):
            return self

        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return instance.staff.call_fn(self, *args, **kwargs)

        return wrapper

    @classmethod
    def complex(cls, overload_param_map: dict[FnOverload, list[str]], behavior: FnBehavior = DEFAULT_BEHAVIOR):
        def wrapper(shape: Callable[Concatenate[Any, P1], R1]) -> Fn[P1, R1]:
            return cls(shape, overload_param_map=overload_param_map, behavior=behavior)  # type: ignore

        return wrapper

    @property
    def has_overload_capability(self) -> bool:
        return bool(self.overload_param_map)

    def collect(
        self,
        collector: BaseCollector,
        **overload_settings: Any,
    ):
        return self.behavior.collect(collector, self, **overload_settings)

    def override(
        self: SupportsCollect[P1, Callable[[Callable[Concatenate[Any, P2], R2]], Any]],  # pyright: ignore
        collector: BaseCollector,
        *args: P1.args,
        **kwargs: P1.kwargs,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P2], R2]) -> OverridePerformEntity[P2, R2]:
            self.collect(collector, *args, **kwargs)(entity)
            return OverridePerformEntity(collector, self, entity)  # type: ignore

        return wrapper
