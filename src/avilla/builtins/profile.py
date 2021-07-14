from dataclasses import dataclass
from typing import Literal, Optional

from avilla.region import Region
from avilla.role import Role
from ..profile import BaseProfile

SexTypes = Literal['male', 'female', 'unknown']

@dataclass
class SelfProfile(BaseProfile):
    "self 只需要有 id(entity) 就可以了, 其他的请自行 fetchdata."
    name: Optional[str] = None

@dataclass
class StrangerProfile(BaseProfile):
    name: str
    sex: SexTypes = 'unknown'
    age: int = None

@dataclass
class FriendProfile(BaseProfile):
    name: str
    remark: str

@dataclass
class GroupProfile(BaseProfile):
    name: str
    counts: Optional[int] = None
    limit: Optional[int] = None

@dataclass
class MemberProfile(BaseProfile):
    id: str
    name: str
    role: Role
    nickname: Optional[str] = None
    title: Optional[str] = None