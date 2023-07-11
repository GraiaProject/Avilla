from typing import Any

from avilla.core._vendor.dataclasses import dataclass, field

from .collector.base import PerformTemplate


@dataclass
class Isolate:
    artifacts: dict[Any, Any] = field(default_factory=dict)

    def apply(self, ring3_class: type[PerformTemplate]):
        arti = ring3_class.__collector__.artifacts
        if "current_collection" in arti:
            self.artifacts.setdefault("lookup_collections", []).append(arti.pop("current_collection"))

        self.artifacts.update(arti)
