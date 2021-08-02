from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel  # pylint: ignore


T_GroupProfile = TypeVar("T_GroupProfile")


class Group(BaseModel, Generic[T_GroupProfile]):
    def __init__(self, id: str, profile: T_GroupProfile):
        super().__init__(id=id, profile=profile)

    id: str
    profile: T_GroupProfile
