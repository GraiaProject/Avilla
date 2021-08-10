from typing import Dict

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.builtins.profile import MemberProfile
from avilla.entity import Entity
from avilla.event import AvillaEvent
from avilla.group import Group
from avilla.typing import T_Profile


class HeartbeatReceived(Dispatchable):
    status: Dict
    interval: int

    def __init__(self, status: Dict, interval: int):
        self.status = status
        self.interval = interval

    def __repr__(self) -> str:
        return f"<HeartbeatReceived: status={self.status} interval={self.interval})>"

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
