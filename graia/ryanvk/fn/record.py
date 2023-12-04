from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterable, MutableMapping, TypedDict

from ryanvk.topic import PileTopic
from ryanvk.typing import Twin

if TYPE_CHECKING:
    from ryanvk.fn.overload import FnOverload

    from .base import Fn


class FnRecord(TypedDict):
    define: Fn
    overload_scopes: dict[str, dict[Any, Any]]
    entities: dict[frozenset[tuple[str, "FnOverload", Any]], Twin]


@dataclass(eq=True, frozen=True)
class FnImplement(PileTopic[FnRecord, tuple[tuple[str, "FnOverload", Any], ...], Twin]):
    fn: Fn

    def iter_entities(self, record: FnRecord) -> MutableMapping[frozenset[tuple[str, "FnOverload", Any]], Twin]:
        return record["entities"]

    def insist_objects(self, record: FnRecord) -> Iterable[Any]:
        return [*record["entities"].keys(), *record["entities"].values()]

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
        return {
            "define": self.fn,
            "overload_scopes": {},
            "entities": {},
        }

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
                    target_set.remove(replacement)

                for k, v in record["entities"].items():
                    if v == replacement:
                        record["entities"][k] = replacement
                        break
                else:
                    raise TypeError

            target_set.add(entity)

        record["entities"][frozenset(signature)] = entity


# TODO: 弃用 Harvest，因为让我很烦。
# 只要只是在 ExtControl 和 Call/Collect Body 之间传递就好，先 make it work.
@dataclass(eq=True, frozen=True)
class FnOverloadHarvest:
    name: str
    overload: FnOverload
    value: Any
