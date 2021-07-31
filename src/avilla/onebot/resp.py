from typing import List, Optional

from pydantic import BaseModel, Field

from avilla.role import Role


class _GetStranger_Resp(BaseModel):
    user_id: str
    nickname: str
    age: Optional[int] = None

    class Config:
        extra = "ignore"


class _GetFriends_Resp_FriendItem(BaseModel):
    user_id: str
    nickname: str
    remark: str


class _GetFriends_Resp(BaseModel):
    __root__: List[_GetFriends_Resp_FriendItem]

    class Config:
        extra = "ignore"


class _GetGroups_Resp_GroupItem(BaseModel):
    group_id: str
    group_name: str
    member_count: int
    max_member_count: int


class _GetGroups_Resp(BaseModel):
    __root__: List[_GetGroups_Resp_GroupItem]

    class Config:
        extra = "ignore"


class _GetMembers_Resp_MemberItem(BaseModel):
    group_id: str
    user_id: str
    name: str = Field(..., alias="nickname")
    nickname: str = Field(..., alias="card")
    role: str
    title: str

    class Config:
        extra = "ignore"


class _GetMembers_Resp(BaseModel):
    __root__: List[_GetMembers_Resp_MemberItem]

    class Config:
        extra = "ignore"
