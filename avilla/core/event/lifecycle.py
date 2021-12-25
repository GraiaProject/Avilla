from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

if TYPE_CHECKING:
    from avilla.core import Avilla


@dataclass
class LifecycleEvent(Dispatchable):
    avilla: "Avilla"

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[LifecycleEvent]"):
            from avilla.core import Avilla

            if interface.annotation is Avilla:
                return interface.event.avilla


class InstanceReady(LifecycleEvent):
    pass


class InstanceShutdown(LifecycleEvent):
    pass
