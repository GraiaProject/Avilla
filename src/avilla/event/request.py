from typing import Any, Literal, Optional

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.entity import Entity
from avilla.group import Group

from ..builtins.profile import GroupProfile, StrangerProfile
from . import AvillaEvent, RelationshipDispatcher


class FriendAddRequest(AvillaEvent[StrangerProfile, Any]):
    comment: Optional[str]
    request_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class GroupJoinRequest(AvillaEvent[StrangerProfile, Any]):  # 主体就是类名第一个名词.
    request_type: Literal["common", "invite"]
    group: Group[GroupProfile]
    comment: Optional[str]
    request_id: str

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher]

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass
