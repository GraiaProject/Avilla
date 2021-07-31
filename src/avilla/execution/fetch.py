from typing import TYPE_CHECKING, Any, Iterable, Union

from pydantic.main import BaseModel

from avilla.builtins.profile import FriendProfile, GroupProfile, MemberProfile, SelfProfile, StrangerProfile
from avilla.group import Group

from ..entity import Entity
from . import Execution, Result


class FetchBot(BaseModel, Result[SelfProfile], Execution[None]):
    pass


class FetchStranger(BaseModel, Result[StrangerProfile], Execution[None]):
    pass


class FetchFriends(BaseModel, Result[Iterable[Entity[FriendProfile]]], Execution[None]):
    pass


class FetchGroup(BaseModel, Result[Group[GroupProfile]], Execution[Union[Group, str]]):
    id: str  # type: ignore


class FetchGroups(BaseModel, Result[Iterable[Group[GroupProfile]]], Execution[None]):
    pass


class FetchMember(BaseModel, Result[Entity[MemberProfile]], Execution[str]):
    group: Union[Group, str]  # type: ignore


class FetchMembers(BaseModel, Result[Iterable[Entity[MemberProfile]]], Execution[Union[Group, str]]):
    pass
