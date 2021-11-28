from dataclasses import dataclass
from datetime import timedelta

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.contactable import Contactable

from ..builtins.profile import (
    FriendProfile,
    GroupProfile,
    MemberProfile,
    StrangerProfile,
)
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
    group: Contactable[GroupProfile]
    file: FileInfo

    Dispatcher = _shared_dispatcher


class MemberPromotedToAdministrator(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]

    Dispatcher = _shared_dispatcher


class MemberDemotedFromAdministrator(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]

    Dispatcher = _shared_dispatcher


class MemberLeave(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]

    Dispatcher = _shared_dispatcher


class MemberRemoved(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]
    operator: Contactable[StrangerProfile]

    Dispatcher = _shared_dispatcher


class MemberJoinedByApprove(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]
    operator: Contactable[MemberProfile]

    Dispatcher = _shared_dispatcher


class MemberJoinedByInvite(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]
    operator: Contactable[MemberProfile]

    Dispatcher = _shared_dispatcher


class MemberMuted(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]
    operator: Contactable[MemberProfile]
    duration: timedelta

    Dispatcher = _shared_dispatcher


class MemberUnmuted(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]
    operator: Contactable[MemberProfile]

    Dispatcher = _shared_dispatcher


class GroupRevoke(AvillaEvent[MemberProfile]):
    group: Contactable[GroupProfile]
    operator: Contactable[MemberProfile]
    message_id: str

    Dispatcher = _shared_dispatcher


class FriendAdd(AvillaEvent[FriendProfile]):  # 好友添加的 Notice.... 怪(因为已经有 Request 了)
    Dispatcher = _shared_dispatcher


class FriendRevoke(AvillaEvent[FriendProfile]):
    message_id: str

    Dispatcher = _shared_dispatcher
