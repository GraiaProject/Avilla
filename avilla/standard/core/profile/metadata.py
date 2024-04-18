from __future__ import annotations

from dataclasses import dataclass

from avilla.core.metadata import Metadata


@dataclass
class Summary(Metadata):
    name: str
    description: str | None


@dataclass
class Nick(Metadata):
    name: str
    nickname: str
    badge: str | None


@dataclass
class Avatar(Metadata):
    url: str
