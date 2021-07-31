from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic.main import BaseModel


T_GroupProfile = TypeVar("T_GroupProfile")


class Group(BaseModel, Generic[T_GroupProfile]):
    id: str
    profile: T_GroupProfile
