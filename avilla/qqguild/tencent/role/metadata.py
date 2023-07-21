from dataclasses import dataclass

from avilla.core.metadata import Metadata
from avilla.core.selector import Selector


@dataclass
class Role(Metadata):
    id: int
    scene: Selector
    name: str
    hoist: bool
    color: int

    def to_selector(self):
        return self.scene.role(str(self.id))
