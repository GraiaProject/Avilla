from dataclasses import dataclass, field
from typing import Any

from .protocol import Ring3

@dataclass
class Isolate:
    artifacts: dict[Any, Any] = field(default_factory=dict)

    def apply(self, ring3_class: type[Ring3]):
        self.artifacts.update(ring3_class.__collector__.artifacts)
