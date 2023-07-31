from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, TypeVar


@dataclass
class PlatformDescription:
    ...


PD = TypeVar("PD", bound=PlatformDescription)


@dataclass
class Platform:
    description: dict[type[PlatformDescription], PlatformDescription]

    def __init__(self, land: Land, abstract: Abstract, *description: PlatformDescription) -> None:
        self.description = {type(i): i for i in description}
        self.description[Land] = land
        self.description[Abstract] = abstract

    def __getitem__(self, item: type[PD]) -> PD:
        return self.description[item]  # type: ignore

    def __str__(self):
        return f"<Platform {' '.join([str(i) for i in self.description.values()])}>"

    @property
    def land(self):
        return self[Land]


class Maintainer(TypedDict):
    name: str


@dataclass
class Land(PlatformDescription):
    name: str
    maintainers: list[Maintainer] = field(default_factory=list)
    humanized_name: str | None = None


@dataclass
class Abstract(PlatformDescription):
    protocol: str
    maintainers: list[Maintainer] = field(default_factory=list)
    humanized_name: str | None = None


@dataclass
class Distribution(PendingDeprecationWarning):
    name: str
    base: str
    maintainers: list[Maintainer] = field(default_factory=list)
    humanized_name: str | None = None


@dataclass
class Branch(PlatformDescription):
    value: str


@dataclass
class Version(PlatformDescription):
    components: dict[str, str]
