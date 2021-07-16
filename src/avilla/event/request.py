from typing import Literal, Optional
from avilla.entity import Entity
from avilla.group import Group
from . import AvillaEvent
from dataclasses import dataclass
from ..builtins.profile import FriendProfile, MemberProfile, StrangerProfile

@dataclass
class FriendAddRequest(AvillaEvent[StrangerProfile, None]):
    target: Entity[StrangerProfile]
    comment: Optional[str]
    request_id: str

@dataclass
class GroupJoinRequest(AvillaEvent[StrangerProfile, None]):
    request_type: Literal['common', 'invite']
    target: Entity[StrangerProfile]
    group: Group
    comment: Optional[str]
    request_id: str

