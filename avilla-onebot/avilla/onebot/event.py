from typing import Dict

from avilla.core.builtins.profile import MemberProfile
from avilla.core.entity import Entity
from avilla.core.event import AvillaEvent
from avilla.core.group import Group
from avilla.core.typing import T_Profile
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface


class HeartbeatReceived(Dispatchable):
    status: Dict
    interval: int

    def __init__(self, status: Dict, interval: int):
        self.status = status
        self.interval = interval

    def __repr__(self) -> str:
        return f"<HeartbeatReceived: status={self.status} interval={self.interval})>"

    @staticmethod
    def get_ability_id() -> str:
        return "event::HeartbeatReceived"

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface):
            return


class NudgeEvent(AvillaEvent[T_Profile]):
    group: Group
    operator: Entity[MemberProfile]

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[NudgeEvent]"):
            if interface.annotation is Group:
                return interface.event.group
