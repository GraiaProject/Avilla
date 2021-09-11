from dataclasses import dataclass
from typing import Generic, TypeVar
from .profile import BaseProfile


T = TypeVar("T", bound=BaseProfile)


@dataclass
class Contactable(Generic[T]):
    id: str
    profile: T


@dataclass
class ref:
    id: str
    type: str
