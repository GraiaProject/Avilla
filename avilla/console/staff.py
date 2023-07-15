from __future__ import annotations

from avilla.core.ryanvk.staff import Staff

from avilla.console.element import ConsoleElement
from avilla.console.frontend.info import Event as ConsoleEvent


class ConsoleStaff(Staff[ConsoleElement, ConsoleEvent]):
    def get_element_type(self, raw_element: ConsoleElement):
        return type(raw_element).__name__
