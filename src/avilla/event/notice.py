from dataclasses import dataclass
from datetime import timedelta

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.entity import Entity
from avilla.group import Group

from ..builtins.profile import FriendProfile, GroupProfile, MemberProfile
from . import AvillaEvent, RelationshipDispatcher


@dataclass
class FileInfo:
    id: str
    name: str
    size: int


@dataclass
class GroupFileUploadNotice(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    file: FileInfo

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class MemberPromotedToAdministrator(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class MemberDemotedFromAdministrator(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class MemberLeave(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class MemberRemoved(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[None]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class MemberJoinedByApprove(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class MemberJoinedByInvite(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class MemberMuted(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[MemberProfile]
    duration: timedelta

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class GroupRevoke(AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[MemberProfile, GroupProfile]
    operator: Entity[None]
    message_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class FriendAdd(AvillaEvent[FriendProfile, None]):  # 好友添加的 Notice.... 怪(因为已经有 Request 了)
    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class FriendRevoke(AvillaEvent[FriendProfile, None]):
    message_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass
