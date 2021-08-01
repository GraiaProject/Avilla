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

    def __init__(self, group: Union[Group, str], target: Union[Entity[MemberProfile], str]):
        super().__init__(group=group, target=target)


class MemberMute(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore
    duration: int  # type: ignore

    def __init__(self, group: Union[Group, str], target: Union[Entity[MemberProfile], str], duration: int):
        super().__init__(group=group, target=target, duration=duration)


class MemberUnmute(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore

    def __init__(self, group: Union[Group, str], target: Union[Entity[MemberProfile], str]):
        super().__init__(group=group, target=target)


class GroupMute(Operation, GroupExecution):  # 群组级别的禁言, MuteAll
    def __init__(self, group: Union[Group, str]):
        super().__init__(target=group)


class GroupUnmute(Operation, GroupExecution):
    def __init__(self, group: Union[Group, str]):
        super().__init__(target=group)


class MemberPromoteToAdministrator(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore

    def __init__(self, group: Union[Group, str], target: Union[Entity[MemberProfile], str]):
        super().__init__(group=group, target=target)


class MemberDemoteFromAdministrator(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore

    def __init__(self, group: Union[Group, str], target: Union[Entity[MemberProfile], str]):
        super().__init__(group=group, target=target)


class MemberNicknameSet(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore
    nickname: str  # type: ignore

    def __init__(self, group: Union[Group, str], target: Union[Entity[MemberProfile], str], nickname: str):
        super().__init__(group=group, target=target, nickname=nickname)


class MemberNicknameClear(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore

    def __init__(self, group: Union[Group, str], target: Union[Entity[MemberProfile], str]):
        super().__init__(group=group, target=target)


class GroupNameSet(Operation, GroupExecution):
    name: str  # type: ignore

    def __init__(self, group: Union[Group, str], name: str):
        super().__init__(target=group, name=name)


class GroupLeave(Operation, GroupExecution):
    group: Union[Group, str]  # type: ignore

    def __init__(self, group: Union[Group, str]):
        super().__init__(target=group)


class MemberSpecialTitleSet(Operation, MemberExecution):
    group: Union[Group, str]  # type: ignore
    title: str  # type: ignore

    def __init__(self, group: Union[Group, str], target: Union[Entity[MemberProfile], str], title: str):
        super().__init__(group=group, target=target, title=title)
