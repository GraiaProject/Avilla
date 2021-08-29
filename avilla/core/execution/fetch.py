from typing import Iterable, Union

from avilla.core.builtins.profile import (FriendProfile, MemberProfile,
                                          SelfProfile, StrangerProfile)
from avilla.core.group import Group

from ..entity import Entity
from . import Execution, Result, auto_update_forward_refs


@auto_update_forward_refs
class FetchBot(Result[SelfProfile], Execution):
    def __init__(self) -> None:
        super().__init__()


@auto_update_forward_refs
class FetchStranger(Result[StrangerProfile], Execution):
    target: str

    def __init__(self, target: str) -> None:
        super().__init__(target=target)


@auto_update_forward_refs
class FetchFriend(Result[Entity[FriendProfile]], Execution):
    target: str

    def __init__(self, target: str) -> None:
        super().__init__(target=target)


@auto_update_forward_refs
class FetchFriends(Result[Iterable[Entity[FriendProfile]]], Execution):
    def __init__(self) -> None:
        super().__init__()


@auto_update_forward_refs
class FetchGroup(Result[Group], Execution):
    target: Union[Group, str]

    def __init__(self, target: Union[Group, str]) -> None:
        super().__init__(target=target)


@auto_update_forward_refs
class FetchGroups(Execution):
    def __init__(self) -> None:
        super().__init__()


@auto_update_forward_refs
class FetchMember(Result[Entity[MemberProfile]], Execution):
    group: Union[Group, str]
    target: str

    def __init__(self, group: Union[Group, str], target: str) -> None:
        super().__init__(target=target, group=group)


@auto_update_forward_refs
class FetchMembers(Result[Iterable[Entity[MemberProfile]]], Execution):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str]) -> None:
        super().__init__(group=group)


@auto_update_forward_refs
class FetchAvatar(Execution):
    target: Union[Group, Entity]

    def __init__(self, target: Union[Group, Entity]) -> None:
        super().__init__(target=target)
