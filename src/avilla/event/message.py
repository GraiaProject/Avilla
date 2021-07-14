from enum import Enum
from typing import Literal, Union
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.entities.dispatcher import BaseDispatcher
from dataclasses import Field, dataclass
from datetime import datetime

from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from avilla.entity import Entity
from avilla.group import Group, T_GroupProfile

from avilla.protocol import T_Profile
from . import AvillaEvent, RelationshipDispatcher, MessageChainDispatcher
from avilla.message.chain import MessageChain
from avilla.region import Region
from avilla.builtins.profile import FriendProfile, GroupProfile, MemberProfile
from avilla.context import ctx_relationship


@dataclass(init=False)
class MessageEvent(AvillaEvent[T_Profile, T_GroupProfile]):
    message: MessageChain
    id: str
    _id_region = Region("Message")

    ## sender: see [AvillaEvent]

    current_id: str  # = Field(default_factory=lambda: ctx_relationship.get().current.id)
    time: datetime  # = Field(default_factory=datetime.now)

    def __init__(
        self,
        entity_or_group: Union[Entity[T_Profile], Group[T_Profile, T_GroupProfile]],
        message: MessageChain,
        message_id: str,
        current_id: str = None,
        time: datetime = None,
    ) -> None:
        self.entity_or_group = entity_or_group
        self.message = message
        self.id = message_id
        self.current_id = current_id or ctx_relationship.get().current.id
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        mixin = [RelationshipDispatcher, MessageChainDispatcher]

        async def catch(interface: "DispatcherInterface"):
            pass


@dataclass
class FriendMessage(MessageEvent[FriendProfile, None]):
    pass


@dataclass
class TempMessage(MessageEvent[MemberProfile, GroupProfile]):
    pass


@dataclass(init=False)
class GroupMessage(MessageEvent[MemberProfile, GroupProfile]):
    subtype: Literal["normal", "anonymous", "notice"]

    def __init__(
        self,
        entity_or_group: Union[Entity[T_Profile], Group[T_Profile, T_GroupProfile]],
        message: MessageChain,
        message_id: str,
        current_id: str = None,
        time: datetime = None,
        subtype: Literal["normal", "anonymous", "notice"] = 'normal'
    ) -> None:
        self.subtype = subtype
        super().__init__(entity_or_group, message, message_id, current_id=current_id, time=time)

    @property
    def is_anonymous(self):
        return self.subtype == "anonymous"

    @property
    def is_notice(self):
        return self.subtype == "notice"
