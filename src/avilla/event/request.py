from typing import TYPE_CHECKING, Literal, Optional
from pydantic import BaseModel

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.entity import Entity
from avilla.group import Group

from ..builtins.profile import FriendProfile, MemberProfile, StrangerProfile
from . import AvillaEvent, RelationshipDispatcher


class FriendAddRequest(AvillaEvent[StrangerProfile, None]):
    comment: Optional[str]
    request_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class GroupJoinRequest(AvillaEvent[StrangerProfile, None]):  # 主体就是类名第一个名词.
    request_type: Literal["common", "invite"]
    target: Entity[StrangerProfile]
    comment: Optional[str]
    request_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass
