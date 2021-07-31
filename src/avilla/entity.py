from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic.main import BaseModel


P = TypeVar("P")


class Entity(BaseModel, Generic[P]):
    id: str
    profile: P
