import typing
from typing import Dict

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.builtins.profile import GroupProfile, MemberProfile
from avilla.core.contactable import Contactable
from avilla.core.event import AvillaEvent
from avilla.core.typing import T_Profile


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
    group: Contactable[GroupProfile]
    operator: Contactable[MemberProfile]

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[NudgeEvent]"):
            if (
                typing.get_origin(interface.annotation) is Contactable
                and (*typing.get_args(interface.annotation), None)[0] is GroupProfile
            ):
                return interface.event.group
