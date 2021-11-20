from typing import Any, Generic, TypeVar

from pydantic.main import BaseModel

from .profile import BaseProfile

T = TypeVar("T", BaseProfile, Any)


class Contactable(Generic[T], BaseModel):
    id: str
    profile: T

    def __init__(self, id: str, profile: T):
        super().__init__(id=id, profile=profile)
