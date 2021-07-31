from dataclasses import Field, dataclass
from datetime import datetime
from enum import Enum
from typing import Literal, Union

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from pydantic.main import BaseModel

from avilla.builtins.profile import FriendProfile, GroupProfile, MemberProfile
from avilla.context import ctx_relationship
from avilla.entity import Entity
from avilla.group import Group, T_GroupProfile
from avilla.message.chain import MessageChain
from avilla.protocol import T_Profile

from . import AvillaEvent, MessageChainDispatcher, RelationshipDispatcher


@dataclass(init=False)
class MessageEvent(AvillaEvent[T_Profile, T_GroupProfile]):
    message: MessageChain
    id: str

    ## sender: see [AvillaEvent]

    def __init__(
        self,
        entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]],
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

        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass


class FriendMessage(BaseModel, MessageEvent[FriendProfile, None]):
    pass


class TempMessage(BaseModel, MessageEvent[MemberProfile, GroupProfile]):
    pass


T_GroupMessageSubType = Literal["common", "anonymous", "notice"]


@dataclass(init=False)
class GroupMessage(MessageEvent[MemberProfile, GroupProfile]):
    subtype: T_GroupMessageSubType

    def __init__(
        self,
        entity_or_group: Union[Entity[T_Profile], Group[T_GroupProfile]],
        message: MessageChain,
        message_id: str,
        current_id: str = None,
        time: datetime = None,
        subtype: T_GroupMessageSubType = "common",
    ) -> None:
        self.subtype = subtype
        super().__init__(entity_or_group, message, message_id, current_id=current_id, time=time)

    @property
    def is_anonymous(self):
        return self.subtype == "anonymous"

    @property
    def is_notice(self):
        return self.subtype == "notice"
