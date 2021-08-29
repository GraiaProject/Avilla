from dataclasses import dataclass
from datetime import timedelta

from avilla.core.entity import Entity
from avilla.core.group import Group
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from ..builtins.profile import FriendProfile, MemberProfile
from . import AvillaEvent, RelationshipDispatcher


@dataclass
class FileInfo:
    id: str
    name: str
    size: int


class _shared_dispatcher(BaseDispatcher):
    mixin = [RelationshipDispatcher]

    @staticmethod
    async def catch(interface: "DispatcherInterface"):
        pass


class GroupFileUploadNotice(AvillaEvent[MemberProfile]):
    group: Group
    file: FileInfo

    Dispatcher = _shared_dispatcher


class MemberPromotedToAdministrator(AvillaEvent[MemberProfile]):
    group: Group

    Dispatcher = _shared_dispatcher


class MemberDemotedFromAdministrator(AvillaEvent[MemberProfile]):
    group: Group

    Dispatcher = _shared_dispatcher


class MemberLeave(AvillaEvent[MemberProfile]):
    group: Group

    Dispatcher = _shared_dispatcher


class MemberRemoved(AvillaEvent[MemberProfile]):
    group: Group
    operator: Entity[None]

    Dispatcher = _shared_dispatcher


class MemberJoinedByApprove(AvillaEvent[MemberProfile]):
    group: Group
    operator: Entity[MemberProfile]

    Dispatcher = _shared_dispatcher


class MemberJoinedByInvite(AvillaEvent[MemberProfile]):
    group: Group
    operator: Entity[MemberProfile]

    Dispatcher = _shared_dispatcher


class MemberMuted(AvillaEvent[MemberProfile]):
    group: Group
    operator: Entity[MemberProfile]
    duration: timedelta

    Dispatcher = _shared_dispatcher


class MemberUnmuted(AvillaEvent[MemberProfile]):
    group: Group
    operator: Entity[MemberProfile]

    Dispatcher = _shared_dispatcher


class GroupRevoke(AvillaEvent[MemberProfile]):
    group: Group
    operator: Entity[None]
    message_id: str

    Dispatcher = _shared_dispatcher


class FriendAdd(AvillaEvent[FriendProfile]):  # 好友添加的 Notice.... 怪(因为已经有 Request 了)
    Dispatcher = _shared_dispatcher


class FriendRevoke(AvillaEvent[FriendProfile]):
    message_id: str

    Dispatcher = _shared_dispatcher
