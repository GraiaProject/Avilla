from typing import Iterable, Union

from avilla.builtins.profile import (FriendProfile, MemberProfile, SelfProfile,
                                     StrangerProfile)
from avilla.group import Group
from avilla.provider import Provider
from avilla.resource import Resource

from ..entity import Entity
from . import Execution, Result, auto_update_forward_refs


@auto_update_forward_refs
class FetchBot(Result[SelfProfile], Execution[None]):
    def __init__(self) -> None:
        super().__init__()


@auto_update_forward_refs
class FetchStranger(Result[StrangerProfile], Execution[str]):
    def __init__(self, target: str) -> None:
        super().__init__(target=target)


@auto_update_forward_refs
class FetchFriend(Result[Entity[FriendProfile]], Execution[str]):
    def __init__(self, target: str) -> None:
        super().__init__(target=target)


@auto_update_forward_refs
class FetchFriends(Result[Iterable[Entity[FriendProfile]]], Execution[None]):
    def __init__(self) -> None:
        super().__init__()


@auto_update_forward_refs
class FetchGroup(Result[Group], Execution[Union[Group, str]]):
    def __init__(self, target: Union[Group, str]) -> None:
        super().__init__(target=target)


@auto_update_forward_refs
class FetchGroups(Execution[None], Result[Iterable[Group]]):
    def __init__(self) -> None:
        super().__init__()


@auto_update_forward_refs
class FetchMember(Result[Entity[MemberProfile]], Execution[str]):
    group: Union[Group, str]

    def __init__(self, group: Union[Group, str], target: str) -> None:
        super().__init__(target=target, group=group)


@auto_update_forward_refs
class FetchMembers(Result[Iterable[Entity[MemberProfile]]], Execution[Union[Group, str]]):
    def __init__(self, target: Union[Group, str]) -> None:
        super().__init__(target=target)


@auto_update_forward_refs
class FetchAvatar(Execution[Union[Group, Entity, None]], Result[Resource[Provider[bytes]]]):
    def __init__(self, target: Union[Group, Entity, None]) -> None:
        super().__init__(target=target)
