from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .collector import BaseCollector


class FnOverload:
    identity: str = "native"

    def collect_entity(
        self,
        collector: BaseCollector,
        scope: dict[Any, Any],
        entity: Any,
        params: dict[str, Any],
    ) -> None:
        scope["_"] = {(collector, entity)}

    def get_entities(self, scope: dict[Any, Any], args: dict[str, Any]) -> set[Callable]:
        return scope["_"]
