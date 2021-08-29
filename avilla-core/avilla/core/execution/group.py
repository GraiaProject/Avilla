from typing import Union

from avilla.core.entity import Entity, EntityPtr

from ..group import Group, GroupPtr
from . import Execution, Operation, auto_update_forward_refs


@auto_update_forward_refs
class MemberRemove(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    member: Union[Entity, EntityPtr, str]

    def __init__(self, group: Union[Group, GroupPtr, str], member: Union[Entity, EntityPtr, str]):
        super().__init__(group=group, member=member)


@auto_update_forward_refs
class MemberMute(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    target: Union[Entity, EntityPtr, str]
    duration: int

    def __init__(
        self,
        group: Union[Group, GroupPtr, str],
        target: Union[Entity, EntityPtr, str],
        duration: int,
    ):
        super().__init__(group=group, target=target, duration=duration)


@auto_update_forward_refs
class MemberUnmute(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    target: Union[Entity, EntityPtr, str]

    def __init__(self, group: Union[Group, GroupPtr, str], target: Union[Entity, EntityPtr, str]):
        super().__init__(group=group, target=target)


@auto_update_forward_refs
class GroupMute(Operation, Execution):  # 群组级别的禁言, MuteAll
    group: Union[Group, GroupPtr, str]

    def __init__(self, group: Union[Group, GroupPtr, str]):
        super().__init__(group=group)


@auto_update_forward_refs
class GroupUnmute(Operation, Execution):
    group: Union[Group, GroupPtr, str]

    def __init__(self, group: Union[Group, GroupPtr, str]):
        super().__init__(group=group)


@auto_update_forward_refs
class MemberPromoteToAdministrator(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    target: Union[Entity, EntityPtr, str]

    def __init__(self, group: Union[Group, GroupPtr, str], target: Union[Entity, EntityPtr, str]):
        super().__init__(group=group, target=target)


@auto_update_forward_refs
class MemberDemoteFromAdministrator(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    target: Union[Entity, EntityPtr, str]

    def __init__(self, group: Union[Group, GroupPtr, str], target: Union[Entity, EntityPtr, str]):
        super().__init__(group=group, target=target)


@auto_update_forward_refs
class MemberNicknameSet(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    target: Union[Entity, EntityPtr, str]
    nickname: str

    def __init__(
        self,
        group: Union[Group, GroupPtr, str],
        target: Union[Entity, EntityPtr, str],
        nickname: str,
    ):
        super().__init__(group=group, target=target, nickname=nickname)


@auto_update_forward_refs
class MemberNicknameClear(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    target: Union[Entity, EntityPtr, str]

    def __init__(self, group: Union[Group, GroupPtr, str], target: Union[Entity, EntityPtr, str]):
        super().__init__(group=group, target=target)


@auto_update_forward_refs
class GroupNameSet(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    name: str

    def __init__(self, group: Union[Group, GroupPtr, str], name: str):
        super().__init__(group=group, name=name)


@auto_update_forward_refs
class GroupLeave(Operation, Execution):
    group: Union[Group, GroupPtr, str]

    def __init__(self, group: Union[Group, GroupPtr, str]):
        super().__init__(group=group)


@auto_update_forward_refs
class MemberSpecialTitleSet(Operation, Execution):
    group: Union[Group, GroupPtr, str]
    target: Union[Entity, EntityPtr, str]
    title: str

    def __init__(
        self, group: Union[Group, GroupPtr, str], target: Union[Entity, EntityPtr, str], title: str
    ):
        super().__init__(group=group, target=target, title=title)
