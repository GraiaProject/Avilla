from __future__ import annotations

from typing import TYPE_CHECKING

from launart.service import ExportInterface

if TYPE_CHECKING:
    from .service import OneBot11Service


class OneBot11Interface(ExportInterface["OneBot11Service"]):
    pass
