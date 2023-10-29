from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from avilla.core.metadata import Metadata
from avilla.core.selector import Selector


@dataclass
class Audit(Metadata):
    id: str
    scene: Selector
    seq: str
    create_time: datetime
    audit_time: datetime
    message: Optional[Selector] = None

    def to_selector(self):
        return self.scene.audit(self.id)
