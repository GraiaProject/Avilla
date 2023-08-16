from __future__ import annotations

from typing import TYPE_CHECKING

from graia.ryanvk import Access

if TYPE_CHECKING:
    from .service import NoneBridgeService


def service():
    instance = Access[NoneBridgeService]()

    instance.__set_name__ = lambda owner, name: None
    instance.name = "nonebridge.service"

    return instance
