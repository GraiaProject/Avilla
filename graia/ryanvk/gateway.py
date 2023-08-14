from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .perform import BasePerform
    from .staff import Staff


class Gateway:
    registry: dict[type[BasePerform], Staff]

    def __init__(self) -> None:
        self.registry = {}

    def register(self, staff: Staff, *perform_types: type[BasePerform]):
        for perform_type in perform_types:
            self.registry[perform_type] = staff


GLOBAL_GATEWAY = Gateway()
