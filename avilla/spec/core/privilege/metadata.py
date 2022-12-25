from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from avilla.core.metadata import Metadata


@dataclass
class MuteInfo(Metadata):
    muted: bool
    duration: timedelta
    time: datetime | None = None


@dataclass
class BanInfo(Metadata):
    banned: bool
    duration: timedelta
    time: datetime | None = None


@dataclass
class Privilege(Metadata):
    available: bool
    effective: bool

    duration: timedelta | None = None
