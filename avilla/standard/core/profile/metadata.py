from __future__ import annotations

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.metadata import Metadata


@dataclass
class Summary(Metadata):
    name: str
    description: str | None


@dataclass
class Nick(Metadata):
    name: str
    nickname: str
    badge: str | None
