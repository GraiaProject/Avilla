from dataclasses import dataclass
from typing import Union

from avilla.entity import Entity

from ..group import Group
from . import Operation, TargetTypes


@dataclass
class MemberRemove(Operation):
    group: Union[Group, str]
    target: Union[Entity, str]
    target_type = TargetTypes.RSMEMBER | TargetTypes.ENTITY


@dataclass
class MemberMute(Operation):
    group: Union[Group, str]
    target: Union[Entity, str]
    duration: int
    target_type = TargetTypes.RSMEMBER | TargetTypes.ENTITY


@dataclass
class MemberUnmute(Operation):
    group: Union[Group, str]
    target: Union[Entity, str]
    target_type = TargetTypes.RSMEMBER | TargetTypes.ENTITY


@dataclass
class GroupMute(Operation):  # 群组级别的禁言, MuteAll
    group: Union[Group, str]
    target_type = TargetTypes.GROUP


@dataclass
class GroupUnmute(Operation):
    group: Union[Group, str]
    target_type = TargetTypes.GROUP


@dataclass
class MemberPromoteToAdministrator(Operation):
    group: Union[Group, str]
    target: Union[Entity, str]
    target_type = TargetTypes.RSMEMBER | TargetTypes.GROUP


@dataclass
class MemberDemoteFromAdministrator(Operation):
    group: Union[Group, str]
    target: Union[Entity, str]
    target_type = TargetTypes.RSMEMBER | TargetTypes.GROUP


@dataclass
class MemberNicknameSet(Operation):
    group: Union[Group, str]
    target: Union[Entity, str]
    nickname: str
    target_type = TargetTypes.RSMEMBER | TargetTypes.GROUP


@dataclass
class GroupNameSet(Operation):
    group: Union[Group, str]
    name: str
    target_type = TargetTypes.GROUP


@dataclass
class GroupLeave(Operation):
    group: Union[Group, str]
    target_type = TargetTypes.GROUP | TargetTypes.RS


@dataclass
class MemberSpecialTitleSet(Operation):
    group: Union[Group, str]
    target: Union[Entity, str]
    title: str
    target_type = TargetTypes.GROUP
