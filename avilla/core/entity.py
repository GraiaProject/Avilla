from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel  # pylint: ignore

P = TypeVar("P")


class Entity(BaseModel, Generic[P]):
    def __init__(self, id: str, profile: P):
        super().__init__(id=id, profile=profile)

    id: str
    profile: P

    @classmethod
    def get_ability_id(cls) -> str:
        return "entity"


@dataclass
class EntityPtr:
    id: str
