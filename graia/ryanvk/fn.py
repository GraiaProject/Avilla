from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic

from typing_extensions import Concatenate, ParamSpec, TypeVar

from graia.ryanvk.override import OverridePerformEntity

if TYPE_CHECKING:
    from .capability import Capability
    from .collector import BaseCollector
    from .overload import FnOverload
    from .perform import BasePerform
    from .typing import SupportsCollect


P = ParamSpec("P")
R = TypeVar("R", covariant=True)

T = TypeVar("T")
P1 = ParamSpec("P1")
P2 = ParamSpec("P2")
R2 = TypeVar("R2", covariant=True)
A = TypeVar("A", infer_variance=True)
WrapperCallable = Callable[[A], A]

FnRecord = tuple["BaseCollector", Callable]


@dataclass(eq=True, frozen=True)
class FnImplement:
    owner: type[BasePerform | Capability]
    name: str


class Fn(Generic[P, R]):
    owner: type[BasePerform | Capability]
    name: str
    shape: Callable
    shape_signature: inspect.Signature

    overload_params: dict[str, FnOverload]
    overload_map: dict[FnOverload, list[str]]

    def __init__(
        self,
        shape: Callable[Concatenate[Any, P], R],
        overload_map: dict[FnOverload, list[str]] | None = None,
    ):
        self.shape = shape
        self.shape_signature = inspect.Signature(list(inspect.Signature.from_callable(shape).parameters.values())[1:])
        self.overload_map = overload_map or {}
        self.overload_params = {i: k for k, v in self.overload_map.items() for i in v}

    def __set_name__(self, owner: type[BasePerform], name: str):
        self.owner = owner
        self.name = name

    @classmethod
    def with_overload(cls, overload_map: dict[FnOverload, list[str]]):
        def wrapper(shape: Callable[Concatenate[Any, P], R]):
            return cls(shape, overload_map=overload_map)

        return wrapper

    @property
    def has_overload_capability(self) -> bool:
        return bool(self.overload_map)

    def collect(
        self,
        collector: BaseCollector,
        **overload_settings: Any,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P], R]):
            artifact = collector.artifacts.setdefault(
                FnImplement(self.owner, self.name),
                {
                    "overload_enabled": self.has_overload_capability,
                    "overload_scopes": {},
                },
            )
            if self.has_overload_capability:
                for fn_overload, params in self.overload_map.items():
                    scope = artifact["overload_scopes"].setdefault(fn_overload.identity, {})
                    fn_overload.collect_entity(
                        collector,
                        scope,
                        entity,
                        {param: overload_settings[param] for param in params},
                    )
            else:
                artifact["handler"] = (collector, entity)

            return entity

        return wrapper

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
