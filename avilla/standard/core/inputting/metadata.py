from __future__ import annotations

from dataclasses import dataclass

from avilla.core.metadata import Metadata


@dataclass
class InputtingStatus(Metadata):
    value: bool
