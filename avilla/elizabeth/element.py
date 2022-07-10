from __future__ import annotations

from avilla.core.elements import Image


class FlashImage(Image):
    def __str__(self) -> str:
        return "[$FlashImage]"
