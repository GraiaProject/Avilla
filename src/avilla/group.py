from dataclasses import dataclass
from typing import AsyncIterable, Generic, Iterable, TypeVar

from .entity import Entity

T_EntityProfile = TypeVar("T_EntityProfile")
T_GroupProfile = TypeVar("T_GroupProfile")


@dataclass
class Group(Generic[T_EntityProfile, T_GroupProfile]):
    id: str
    entities: AsyncIterable[Entity[T_EntityProfile]]  # 因为是懒加载.
    profile: T_GroupProfile
