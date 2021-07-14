from dataclasses import dataclass
from typing import Generic, TypeVar

P = TypeVar('P')

@dataclass
class Entity(Generic[P]):
    id: str
    profile: P