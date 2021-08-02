from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel  # pylint: ignore


P = TypeVar("P")


class Entity(BaseModel, Generic[P]):
    def __init__(self, id: str, profile: P):
        super().__init__(id=id, profile=profile)

    id: str
    profile: P
