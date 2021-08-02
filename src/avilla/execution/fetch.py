from typing import Iterable, Union

from avilla.builtins.profile import (
    FriendProfile,
    GroupProfile,
    MemberProfile,
    SelfProfile,
    StrangerProfile,
)
from avilla.group import Group

from ..entity import Entity
from . import Execution, Result


class FetchBot(Result[SelfProfile], Execution[None]):
    def __init__(self) -> None:
        super().__init__()


class FetchStranger(Result[StrangerProfile], Execution[str]):
    def __init__(self, target: str) -> None:
        super().__init__(target=target)


class FetchFriend(Result[Entity[FriendProfile]], Execution[str]):
    def __init__(self, target: str) -> None:
        super().__init__(target=target)


class FetchFriends(Result[Iterable[Entity[FriendProfile]]], Execution[None]):
    def __init__(self) -> None:
        super().__init__()


class FetchGroup(Result[Group[GroupProfile]], Execution[Union[Group, str]]):
    def __init__(self, target: Union[Group, str]) -> None:
        super().__init__(target=target)


class FetchGroups(Execution[None], Result[Iterable[Group[GroupProfile]]]):
    def __init__(self) -> None:
        super().__init__()


class FetchMember(Result[Entity[MemberProfile]], Execution[str]):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str], target: str) -> None:
        super().__init__(target=target, group=group)


class FetchMembers(Result[Iterable[Entity[MemberProfile]]], Execution[Union[Group, str]]):
    def __init__(self, target: Union[Group, str]) -> None:
        super().__init__(target=target)
