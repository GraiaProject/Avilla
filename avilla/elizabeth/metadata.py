from __future__ import annotations

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.metadata import Metadata


@dataclass
class InputtingStatus(Metadata):
    value: bool
