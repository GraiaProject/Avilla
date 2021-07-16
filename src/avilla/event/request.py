from dataclasses import dataclass
from typing import Literal, Optional

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.entity import Entity
from avilla.group import Group

from ..builtins.profile import FriendProfile, MemberProfile, StrangerProfile
from . import AvillaEvent, RelationshipDispatcher


@dataclass
class FriendAddRequest(AvillaEvent[StrangerProfile, None]):
    comment: Optional[str]
    request_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
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
