from __future__ import annotations

from dataclasses import dataclass

from avilla.core.metadata import Metadata


@dataclass
class Count(Metadata):
    current: int
    max: int
