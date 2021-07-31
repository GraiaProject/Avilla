from dataclasses import dataclass

from pydantic.main import BaseModel


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


class GroupFileUploadNotice(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]
    file: FileInfo

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MemberPromotedToAdministrator(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MemberDemotedFromAdministrator(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MemberLeave(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MemberRemoved(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]
    operator: Entity[None]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MemberJoinedByApprove(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MemberJoinedByInvite(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class MemberMuted(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]
    operator: Entity[MemberProfile]
    duration: timedelta

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class GroupRevoke(BaseModel, AvillaEvent[MemberProfile, GroupProfile]):
    group: Group[GroupProfile]
    operator: Entity[None]
    message_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class FriendAdd(BaseModel, AvillaEvent[FriendProfile, None]):  # 好友添加的 Notice.... 怪(因为已经有 Request 了)
    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class FriendRevoke(BaseModel, AvillaEvent[FriendProfile, None]):
    message_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass
