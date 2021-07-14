from dataclasses import dataclass
from typing import Iterable, Generic, Iterable, TypeVar
from .entity import Entity

T_EntityProfile = TypeVar("T_EntityProfile")
T_GroupProfile = TypeVar("T_GroupProfile")


@dataclass
class Group(Generic[T_EntityProfile, T_GroupProfile]):
    id: str
    entities: Iterable[Entity[T_EntityProfile]]
    profile: T_GroupProfile
