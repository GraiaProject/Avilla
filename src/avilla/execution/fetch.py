from typing import TYPE_CHECKING, Any, Iterable, Union

from pydantic.main import BaseModel

from avilla.builtins.profile import FriendProfile, GroupProfile, MemberProfile, SelfProfile, StrangerProfile
from avilla.group import Group

from ..entity import Entity
from . import Execution, Result


class FetchBot(BaseModel, Result[SelfProfile], Execution[None]):
    def __init__(self) -> None:
        super().__init__()


class FetchStranger(BaseModel, Result[StrangerProfile], Execution[str]):
    def __init__(self, target: str) -> None:
        super().__init__(target=target)


class FetchFriends(BaseModel, Result[Iterable[Entity[FriendProfile]]], Execution[None]):
    def __init__(self) -> None:
        super().__init__()


class FetchGroup(BaseModel, Result[Group[GroupProfile]], Execution[Union[Group, str]]):
    def __init__(self, target: Union[Group, str]) -> None:
        super().__init__(target=target)


class FetchGroups(BaseModel, Execution[None], Result[Iterable[Group[GroupProfile]]]):
    def __init__(self) -> None:
        super().__init__()


class FetchMember(BaseModel, Result[Entity[MemberProfile]], Execution[str]):
    group: Union[Group, str]  # type: ignore

    def __init__(self, group: Union[Group, str], target: str) -> None:
        super().__init__(target=target, group=group)


class FetchMembers(BaseModel, Result[Iterable[Entity[MemberProfile]]], Execution[Union[Group, str]]):
    def __init__(self, target: Union[Group, str]) -> None:
        super().__init__(target=target)
