from __future__ import annotations

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.metadata import Metadata


@dataclass
class Status(Metadata):
    name: str
    description: str | None
