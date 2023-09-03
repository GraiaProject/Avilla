from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, TypedDict

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

P1 = ParamSpec("P1")
P2 = ParamSpec("P2")
R2 = TypeVar("R2", covariant=True)


class FnRecord(TypedDict):
    overload_enabled: bool
    overload_scopes: dict[str, dict[Any, Any]]
    handler: Callable | None


class _MergeScopesInfo(TypedDict):
    overload_item: FnOverload
    scopes: list[dict[Any, Any]]


@dataclass(eq=True, frozen=True)
class FnImplement:
    fn: Fn

    def merge(self, *records: FnRecord):
        scopes_info: dict[str, _MergeScopesInfo] = {}
        scopes = {}

        for record in records:
            for k, v in record["overload_scopes"].items():
                overload_item = self.fn.overload_map[k]
                info = scopes_info.setdefault(k, {"overload_item": overload_item, "scopes": []})
                info["scopes"].append(v)

        for identity, info in scopes_info.items():
            merged_scope = info["overload_item"].merge_scopes(*info["scopes"])
            scopes[identity] = merged_scope

        return {
            "overload_enabled": self.fn.has_overload_capability,
            "overload_scopes": scopes,
            "handler": records[-1]["handler"],
        }


class Fn(Generic[P, R]):
    owner: type[BasePerform | Capability]
    name: str
    shape: Callable
    shape_signature: inspect.Signature

    overload_params: dict[str, FnOverload]
    overload_param_map: dict[FnOverload, list[str]]
    overload_map: dict[str, FnOverload]

    def __init__(
        self,
        shape: Callable[Concatenate[Any, P], R],
        overload_param_map: dict[FnOverload, list[str]] | None = None,
    ):
        self.shape = shape
        self.shape_signature = inspect.Signature(list(inspect.Signature.from_callable(shape).parameters.values())[1:])
        self.overload_param_map = overload_param_map or {}
        self.overload_params = {i: k for k, v in self.overload_param_map.items() for i in v}
        self.overload_map = {i.identity: i for i in self.overload_param_map}

    def __set_name__(self, owner: type[BasePerform], name: str):
        self.owner = owner
        self.name = name

    @classmethod
    def with_overload(cls, overload_param_map: dict[FnOverload, list[str]]):
        def wrapper(shape: Callable[Concatenate[Any, P], R]):
            return cls(shape, overload_param_map=overload_param_map)

        return wrapper

    @property
    def has_overload_capability(self) -> bool:
        return bool(self.overload_param_map)

    def collect(
        self,
        collector: BaseCollector,
        **overload_settings: Any,
    ):
        def wrapper(entity: Callable[Concatenate[Any, P], R]):
            artifact = collector.artifacts.setdefault(
                FnImplement(self),
                {
                    "overload_enabled": self.has_overload_capability,
                    "overload_scopes": {},
                    "handler": None,
                },
            )
            if self.has_overload_capability:
                for fn_overload, params in self.overload_param_map.items():
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
