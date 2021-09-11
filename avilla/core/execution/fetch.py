from avilla.core.contactable import Contactable, ref
from typing import Iterable, Union

from avilla.core.builtins.profile import (
    FriendProfile,
    GroupProfile,
    MemberProfile,
    SelfProfile,
    StrangerProfile,
)

from . import Execution, Result


class FetchBot(Result[SelfProfile], Execution):
    def __init__(self) -> None:
        super().__init__()


class FetchStranger(Result[StrangerProfile], Execution):
    target: str

    def __init__(self, target: str) -> None:
        super().__init__(target=target)


class FetchFriend(Result[Contactable[FriendProfile]], Execution):
    target: str

    def __init__(self, target: str) -> None:
        super().__init__(target=target)


class FetchFriends(Result[Iterable[Contactable[FriendProfile]]], Execution):
    def __init__(self) -> None:
        super().__init__()


class FetchGroup(Result[Contactable[GroupProfile]], Execution):
    target: Union[Contactable[GroupProfile], str]

    def __init__(self, target: Union[Contactable[GroupProfile], str]) -> None:
        super().__init__(target=target)


class FetchGroups(Execution):
    def __init__(self) -> None:
        super().__init__()


class FetchMember(Result[Contactable[MemberProfile]], Execution):
    group: Union[Contactable[GroupProfile], str]
    target: str

    def __init__(self, group: Union[Contactable[GroupProfile], str], target: str) -> None:
        super().__init__(target=target, group=group)


class FetchMembers(Result[Iterable[Contactable[MemberProfile]]], Execution):
    group: Union[Contactable[GroupProfile], str]

    def __init__(self, group: Union[Contactable[GroupProfile], str]) -> None:
        super().__init__(group=group)


class FetchAvatar(Execution):
    target: Union[Contactable, ref]

    def __init__(self, target: Union[Contactable, ref]) -> None:
        super().__init__(target=target)
