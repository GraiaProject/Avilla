from __future__ import annotations

from dataclasses import dataclass

from avilla.core.elements import Element
from satori.element import Button as SatoriButton


@dataclass
class Reply(Element):
    id: str


class Button(SatoriButton, Element):
    ...
