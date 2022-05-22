from dataclasses import dataclass
from typing import Dict, Literal, NoReturn, Optional, Type, TypeVar, Union


@dataclass
class PlatformDescription:
    supplier: str  # 供应商
    name: str
    humanized_name: str

    is_runtime: bool = False


PD = TypeVar("PD", bound=PlatformDescription)


@dataclass
class Platform:
    description: Dict[Type[PlatformDescription], PlatformDescription]

    def __init__(self, *description: PlatformDescription) -> None:
        self.description = {type(i): i for i in description}

    def __getitem__(self, item: Type[PD]) -> Union[PD, NoReturn]:
        return self.description[item]  # type: ignore


@dataclass
class Base(PlatformDescription):
    version: Optional[str] = None


@dataclass
class Medium(PlatformDescription):
    generation: Optional[str] = None
    version: Optional[str] = None


@dataclass
class Adapter(PlatformDescription):
    version: Optional[str] = None


@dataclass
class MediumDistribution(PlatformDescription):
    pass
