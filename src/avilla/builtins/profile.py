from typing import TYPE_CHECKING, Literal, Optional

from pydantic.main import BaseModel


from avilla.role import Role

from ..profile import BaseProfile


class SelfProfile(BaseModel, BaseProfile):
    "self 只需要有 id(entity) 就可以了, 其他的请自行 fetchdata."
    name: Optional[str] = None


class StrangerProfile(BaseModel, BaseProfile):
    name: str
    age: int = None


class FriendProfile(BaseModel, BaseProfile):
    name: str
    remark: str


class GroupProfile(BaseModel, BaseProfile):
    name: str
    counts: Optional[int] = None
    limit: Optional[int] = None


class MemberProfile(BaseModel, BaseProfile):
    name: str
    role: Role
    nickname: Optional[str] = None
    title: Optional[str] = None
