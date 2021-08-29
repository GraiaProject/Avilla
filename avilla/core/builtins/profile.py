from typing import TYPE_CHECKING, Optional

from avilla.core.role import Role
from pydantic import BaseModel

from ..profile import BaseProfile

if TYPE_CHECKING:
    from avilla.core.group import Group  # pylint: ignore


class SelfProfile(BaseModel, BaseProfile):
    "self 只需要有 id(entity) 就可以了, 其他的请自行 fetchdata."
    name: Optional[str] = None


class StrangerProfile(BaseModel, BaseProfile):
    name: str
    age: Optional[int] = None


class FriendProfile(BaseModel, BaseProfile):
    name: str
    remark: str


class GroupProfile(BaseModel, BaseProfile):
    name: Optional[str] = None
    counts: Optional[int] = None
    limit: Optional[int] = None


class MemberProfile(BaseModel, BaseProfile):
    name: Optional[str] = None
    group: Optional["Group"] = None
    role: Optional[Role] = None
    nickname: Optional[str] = None
    title: Optional[str] = None


from avilla.core.group import Group  # noqa

MemberProfile.update_forward_refs(Group=Group)
