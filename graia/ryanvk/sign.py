from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, TypedDict

from typing_extensions import ParamSpec, TypeVar

if TYPE_CHECKING:
    from .fn import Fn
    from .overload import FnOverload


P = ParamSpec("P")
R = TypeVar("R", covariant=True)
R1 = TypeVar("R1", covariant=True)

P1 = ParamSpec("P1")
P2 = ParamSpec("P2")
R2 = TypeVar("R2", covariant=True)


class _MergeScopesInfo(TypedDict):
    overload_item: FnOverload
    scopes: list[dict[Any, Any]]


class FnRecord(TypedDict):
    overload_enabled: bool
    overload_scopes: dict[str, dict[Any, Any]]
    record_tuple: Callable | None


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
            "record_tuple": records[-1]["record_tuple"],
        }
