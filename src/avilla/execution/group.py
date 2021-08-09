from typing import Union

from avilla.builtins.profile import MemberProfile
from avilla.entity import Entity

from ..group import Group
from . import Execution, Operation, auto_update_forward_refs

GroupExecution = Execution[Union[Group, str]]
MemberExecution = Execution[Union[Entity[MemberProfile], str]]


@auto_update_forward_refs
class MemberRemove(Operation, MemberExecution):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str]):
        super().__init__(group=group)


@auto_update_forward_refs
class MemberMute(Operation, MemberExecution):
    group: Union[Group, str]
    duration: int

    def __init__(self, group: Union[Group, str], duration: int):
        super().__init__(group=group, duration=duration)


@auto_update_forward_refs
class MemberUnmute(Operation, MemberExecution):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str]):
        super().__init__(group=group)


@auto_update_forward_refs
class GroupMute(Operation, GroupExecution):  # 群组级别的禁言, MuteAll
    pass


@auto_update_forward_refs
class GroupUnmute(Operation, GroupExecution):
    def __init__(self, group: Union[Group, str]):
        super().__init__(target=group)


@auto_update_forward_refs
class MemberPromoteToAdministrator(Operation, MemberExecution):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str]):
        super().__init__(group=group)


@auto_update_forward_refs
class MemberDemoteFromAdministrator(Operation, MemberExecution):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str]):
        super().__init__(group=group)


@auto_update_forward_refs
class MemberNicknameSet(Operation, MemberExecution):
    group: Union[Group, str]
    nickname: str

    def __init__(self, group: Union[Group, str], nickname: str):
        super().__init__(group=group, nickname=nickname)


@auto_update_forward_refs
class MemberNicknameClear(Operation, MemberExecution):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str]):
        super().__init__(group=group)


@auto_update_forward_refs
class GroupNameSet(Operation, GroupExecution):
    name: str

    def __init__(self, group: Union[Group, str], name: str):
        super().__init__(target=group, name=name)


@auto_update_forward_refs
class GroupLeave(Operation, GroupExecution):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str]):
        super().__init__(target=group)


@auto_update_forward_refs
class MemberSpecialTitleSet(Operation, MemberExecution):
    group: Union[Group, str]
    title: str

    def __init__(self, group: Union[Group, str], title: str):
        super().__init__(group=group, title=title)
