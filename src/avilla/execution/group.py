from typing import TYPE_CHECKING, Union

from pydantic.main import BaseModel


from avilla.builtins.profile import MemberProfile
from avilla.entity import Entity

from ..group import Group
from . import Execution, Operation

GroupExecution = Execution[Union[Group, str]]
MemberExecution = Execution[Union[Entity[MemberProfile], str]]


class MemberRemove(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore


class MemberMute(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore
    duration: int  # type: ignore


class MemberUnmute(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore


class GroupMute(Operation, GroupExecution):  # 群组级别的禁言, MuteAll
    group: Union[Group, str]  # type: ignore


class GroupUnmute(Operation, GroupExecution):
    group: Union[Group, str]  # type: ignore


class MemberPromoteToAdministrator(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore


class MemberDemoteFromAdministrator(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore


class MemberNicknameSet(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore
    nickname: str  # type: ignore


class MemberNicknameClear(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore


class GroupNameSet(Operation, GroupExecution):
    group: Union[Group, str]  # type: ignore
    name: str  # type: ignore


class GroupLeave(Operation, GroupExecution):
    group: Union[Group, str]  # type: ignore


class MemberSpecialTitleSet(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore
    title: str  # type: ignore
