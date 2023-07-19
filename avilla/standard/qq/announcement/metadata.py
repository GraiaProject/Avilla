from __future__ import annotations

from datetime import datetime

from avilla.core.selector import Selector
from avilla.core.platform import Land
from avilla.core._vendor.dataclasses import dataclass
from avilla.core.metadata import Metadata


@dataclass(slots=True)
class Announcement(Metadata):
    id: str
    scene: Selector
    sender: Selector
    all_confirmed: bool
    confirmed_members: int
    time: datetime

    @property
    def land(self):
        return Land(self.scene["land"])
    def to_selector(self) -> Selector:
        return self.scene.announcement(self.id)