from __future__ import annotations

from dataclasses import dataclass

from avilla.core.elements import Element


@dataclass
class Reply(Element):
    id: str
