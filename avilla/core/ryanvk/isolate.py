from typing import Any

from avilla.core._vendor.dataclasses import dataclass, field

from .protocol import Ring3


@dataclass
class Isolate:
    artifacts: dict[Any, Any] = field(default_factory=dict)

    def apply(self, ring3_class: type[Ring3]):
        arti: dict = ring3_class.__collector__.artifacts
        if "current_collection" in arti:
            self.artifacts.setdefault("lookup_collections", []).append(arti.pop("current_collection"))

        self.artifacts.update(arti)
