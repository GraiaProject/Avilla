from dataclasses import dataclass
from datetime import timedelta
from avilla.entity import Entity

from avilla.group import Group
from . import AvillaEvent
from ..builtins.profile import FriendProfile, MemberProfile, GroupProfile

@dataclass
class FileInfo:
    id: str
    name: str
    size: int

@dataclass
class GroupFileUploadNotice(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    file: FileInfo

@dataclass
class MemberPromotedToAdministrator(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    target: Entity[MemberProfile]

@dataclass
class MemberDemotedFromAdministrator(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    target: Entity[MemberProfile]

@dataclass
class MemberLeave(AvillaEvent[MemberProfile, GroupProfile]):       
    group: Group[MemberProfile, GroupProfile]
    target: Entity[None]

@dataclass
class MemberRemoved(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[None]
    target: Entity[None]

@dataclass
class MemberJoinedByApprove(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[MemberProfile]
    target: Entity[MemberProfile]

@dataclass
class MemberJoinedByInvite(AvillaEvent[MemberProfile, GroupProfile]):       
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[MemberProfile]
    target: Entity[MemberProfile]

@dataclass
class MemberMuted(AvillaEvent[MemberProfile, GroupProfile]):       
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[MemberProfile]
    target: Entity[MemberProfile]
    duration: timedelta

@dataclass
class GroupRevoke(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[None]
    target: Entity[None]
    message_id: str

@dataclass
class FriendAdd(AvillaEvent[FriendProfile, None]):
    target: Entity[FriendProfile]

@dataclass
class FriendRevoke(AvillaEvent[FriendProfile, None]):
    target: Entity[FriendProfile]
    message_id: str

