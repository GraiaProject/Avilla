from typing import Any, Iterable, Union
from avilla.builtins.profile import (
    FriendProfile,
    MemberProfile,
    SelfProfile,
    StrangerProfile,
    GroupProfile,
)
from avilla.group import Group
from . import Execution, Result, TargetTypes
from dataclasses import dataclass
from ..entity import Entity


@dataclass
class FetchBot(Result[SelfProfile]):
    target_type = TargetTypes.NONE


@dataclass
class FetchStranger(Result[StrangerProfile]):
    target_type = TargetTypes.NONE


@dataclass
class FetchFriends(Result[Iterable[Entity[FriendProfile]]]):
    target_type = TargetTypes.NONE


@dataclass
class FetchGroup(Result[Group[Any, GroupProfile]]):
    id: str
    target_type = TargetTypes.GROUP


@dataclass
class FetchGroups(Result[Iterable[Group[Any, GroupProfile]]]):
    target_type = TargetTypes.NONE


@dataclass
class FetchMember(Result[Entity[MemberProfile]]):
    group: Union[Group, str]
    member: Union[Entity, str]
    target_type = TargetTypes.CTX


@dataclass
class FetchMembers(Result[Iterable[Entity[MemberProfile]]]):
    group: Union[Group, str]
    target_type = TargetTypes.GROUP
