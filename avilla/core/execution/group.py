from typing import Union

from avilla.core.builtins.profile import GroupProfile, MemberProfile
from avilla.core.contactable import Contactable, ref

from . import Execution, Operation


class MemberRemove(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    member: Union[Contactable[MemberProfile], ref, str]

    def __init__(
        self,
        group: Union[Contactable[GroupProfile], ref, str],
        member: Union[Contactable[MemberProfile], ref, str],
    ):
        super().__init__(group=group, member=member)


class MemberMute(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    target: Union[Contactable[MemberProfile], ref, str]
    duration: int

    def __init__(
        self,
        group: Union[Contactable[GroupProfile], ref, str],
        target: Union[Contactable[MemberProfile], ref, str],
        duration: int,
    ):
        super().__init__(group=group, target=target, duration=duration)


class MemberUnmute(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    target: Union[Contactable[MemberProfile], ref, str]

    def __init__(
        self,
        group: Union[Contactable[GroupProfile], ref, str],
        target: Union[Contactable[MemberProfile], ref, str],
    ):
        super().__init__(group=group, target=target)


class GroupMute(Operation, Execution):  # 群组级别的禁言, MuteAll
    group: Union[Contactable[GroupProfile], ref, str]

    def __init__(self, group: Union[Contactable[GroupProfile], ref, str]):
        super().__init__(group=group)


class GroupUnmute(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]

    def __init__(self, group: Union[Contactable[GroupProfile], ref, str]):
        super().__init__(group=group)


class MemberPromoteToAdministrator(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    target: Union[Contactable[MemberProfile], ref, str]

    def __init__(
        self,
        group: Union[Contactable[GroupProfile], ref, str],
        target: Union[Contactable[MemberProfile], ref, str],
    ):
        super().__init__(group=group, target=target)


class MemberDemoteFromAdministrator(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    target: Union[Contactable[MemberProfile], ref, str]

    def __init__(
        self,
        group: Union[Contactable[GroupProfile], ref, str],
        target: Union[Contactable[MemberProfile], ref, str],
    ):
        super().__init__(group=group, target=target)


class MemberNicknameSet(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    target: Union[Contactable[MemberProfile], ref, str]
    nickname: str

    def __init__(
        self,
        group: Union[Contactable[GroupProfile], ref, str],
        target: Union[Contactable[MemberProfile], ref, str],
        nickname: str,
    ):
        super().__init__(group=group, target=target, nickname=nickname)


class MemberNicknameClear(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    target: Union[Contactable[MemberProfile], ref, str]

    def __init__(
        self,
        group: Union[Contactable[GroupProfile], ref, str],
        target: Union[Contactable[MemberProfile], ref, str],
    ):
        super().__init__(group=group, target=target)


class GroupNameSet(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    name: str

    def __init__(self, group: Union[Contactable[GroupProfile], ref, str], name: str):
        super().__init__(group=group, name=name)


class GroupLeave(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]

    def __init__(self, group: Union[Contactable[GroupProfile], ref, str]):
        super().__init__(group=group)


class MemberSpecialTitleSet(Operation, Execution):
    group: Union[Contactable[GroupProfile], ref, str]
    target: Union[Contactable[MemberProfile], ref, str]
    title: str

    def __init__(
        self,
        group: Union[Contactable[GroupProfile], ref, str],
        target: Union[Contactable[MemberProfile], ref, str],
        title: str,
    ):
        super().__init__(group=group, target=target, title=title)

    class Config:
        arbitrary_types_allowed = True
