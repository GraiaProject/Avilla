from __future__ import annotations

from dataclasses import dataclass

from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.event import AvillaEvent
from avilla.core.selector import Selector


@dataclass
class ActivityEvent(AvillaEvent):
    id: str  # eg. "button_clicked"
    scene: Selector
    activity: Selector  # eg. [...].button("#1")

    def to_selector(self):  # eg. [...].activity("button_clicked")
        return self.scene.activity(self.id)

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[ActivityEvent]):
            if interface.name == "activity":
                return interface.event.to_selector()
            return await AvillaEvent.Dispatcher.catch(interface)


@dataclass
class ActivityAvailable(ActivityEvent):
    pass


@dataclass
class ActivityUnavailable(ActivityEvent):
    pass


@dataclass
class ActivityTrigged(ActivityEvent):
    trigger: Selector  # who trigged the activity

    class Dispatcher(ActivityEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[ActivityTrigged]):
            if interface.name == "trigger":
                return interface.event.trigger
            return await ActivityEvent.Dispatcher.catch(interface)
