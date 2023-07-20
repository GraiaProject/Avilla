from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avilla.core.metadata import Metadata
from avilla.core.platform import Land
from avilla.core.selector import Selector


@dataclass
class Announcement(Metadata):
    id: str
    scene: Selector
    sender: Selector
    content: str
    all_confirmed: bool
    confirmed_members: int
    time: datetime

    @property
    def land(self):
        return Land(self.scene["land"])

    def to_selector(self) -> Selector:
        return self.scene.announcement(self.id)
