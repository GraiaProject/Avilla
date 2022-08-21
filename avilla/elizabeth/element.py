from __future__ import annotations

from avilla.core.elements import Picture


class FlashImage(Picture):
    def __str__(self) -> str:
        return "[$FlashImage]"
