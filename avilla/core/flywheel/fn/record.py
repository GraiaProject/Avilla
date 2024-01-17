from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypedDict

from ..topic import PileTopic
from ..typing import Twin

if TYPE_CHECKING:
    from .base import Fn
    from .overload import FnOverload


class FnRecord(TypedDict):
    define: Fn
    overload_scopes: dict[str, dict[Any, Any]]
    entities: dict[frozenset[tuple[str, "FnOverload", Any]], Twin]


@dataclass(eq=True, frozen=True)
class FnImplement(PileTopic):
    fn: Fn

    def iter_entities(self, record: FnRecord):
        return record["entities"]

    def has_entity(
        self,
        record: FnRecord,
        signature: tuple[tuple[str, "FnOverload", Any], ...],
    ) -> bool:
        return signature in record["entities"]

    def get_entity(
        self,
        record: FnRecord,
        signature: frozenset[tuple[str, "FnOverload", Any]],
    ) -> Twin:
        return record["entities"][signature]

    def new_record(self) -> FnRecord:
        return {"define": self.fn, "overload_scopes": {}, "entities": {}}

    def flatten_record(self, record: FnRecord, target: FnRecord) -> None:
        target["define"] = record["define"]

    def flatten_entity(
        self,
        record: FnRecord,
        signature: tuple[tuple[str, "FnOverload", Any], ...],
        entity: Twin,
        replacement: Twin | None,
    ) -> None:
        scopes = record["overload_scopes"]
        for segment in signature:
            name, fn_overload, sign = segment
            if name not in scopes:
                scope = scopes[name] = {}
            else:
                scope = scopes[name]

            target_set = fn_overload.collect(scope, sign)
            if replacement is not None:
                if replacement in target_set:
                    del target_set[replacement]

                for k, v in record["entities"].items():
                    if v == replacement:
                        record["entities"][k] = replacement
                        break
                else:
                    raise TypeError

            target_set[entity] = None

        record["entities"][frozenset(signature)] = entity


@dataclass(eq=True, frozen=True)
class FnOverloadHarvest:
    name: str
    overload: FnOverload
    value: Any
