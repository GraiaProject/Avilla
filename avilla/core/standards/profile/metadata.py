from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from ...abstract.metadata import Metadata


@dataclass
class Summary(Metadata):
    name: str
    description: str | None


@dataclass
class Nick(Metadata):
    name: str
    nickname: str
    badge: str | None
