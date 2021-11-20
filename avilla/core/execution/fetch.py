from typing import Iterable

from avilla.core.builtins.profile import (
    FriendProfile,
    GroupProfile,
    MemberProfile,
    SelfProfile,
    StrangerProfile,
)
from avilla.core.contactable import Contactable

from . import Execution, Result


class FetchBot(Result[SelfProfile], Execution):
    pass


class FetchStranger(Result[StrangerProfile], Execution):
    target: str

    def __init__(self, target: str) -> None:
        super().__init__(target=target)


class FetchFriend(Result[Contactable[FriendProfile]], Execution):
    target: str

    def __init__(self, target: str) -> None:
        super().__init__(target=target)


class FetchFriends(Result[Iterable[Contactable[FriendProfile]]], Execution):
    pass


class FetchGroup(Result[Contactable[GroupProfile]], Execution):
    class Config:
        arbitrary_types_allowed = True


class FetchGroups(Execution):
    pass


class FetchMember(Result[Contactable[MemberProfile]], Execution):
    target: str

    def __init__(self, target: str) -> None:
        super().__init__(target=target)

    class Config:
        arbitrary_types_allowed = True


class FetchMembers(Result[Iterable[Contactable[MemberProfile]]], Execution):
    class Config:
        arbitrary_types_allowed = True


class FetchAvatar(Execution):
    pass
