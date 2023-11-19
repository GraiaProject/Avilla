from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from avilla.core import Land, Metadata, Selector


class PollKind(str, Enum):
    REGULAR = "regular"
    QUIZ = "quiz"


@dataclass
class Poll(Metadata):
    id: str
    scene: Selector
    question: str
    options: list[str]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    kind: PollKind

    @property
    def land(self):
        return Land(self.scene["land"])

    def to_selector(self) -> Selector:
        return self.scene.announcement(self.id)
