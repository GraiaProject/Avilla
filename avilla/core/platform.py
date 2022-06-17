from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar


@dataclass
class PlatformDescription:
    supplier: str  # 供应商
    name: str
    humanized_name: str

    is_runtime: bool = False


PD = TypeVar("PD", bound=PlatformDescription)


@dataclass
class Platform:
    description: dict[type[PlatformDescription], PlatformDescription]

    def __init__(self, *description: PlatformDescription) -> None:
        self.description = {type(i): i for i in description}

    def __getitem__(self, item: type[PD]) -> PD:
        return self.description[item]  # type: ignore


@dataclass
class Base(PlatformDescription):
    version: str | None = None


@dataclass
class Medium(PlatformDescription):
    generation: str | None = None
    version: str | None = None


@dataclass
class Adapter(PlatformDescription):
    version: str | None = None


@dataclass
class MediumDistribution(PlatformDescription):
    pass
