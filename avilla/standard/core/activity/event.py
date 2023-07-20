from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.event import AvillaEvent
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface


@dataclass
class ActivityEvent(AvillaEvent):
    id: Selector  # eg. [...].activity("button_clicked")
    activity: Selector  # eg. [...].button("#1")

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface[ActivityEvent]):
            ...


@dataclass
class ActivityAvailable(ActivityEvent):
    pass


@dataclass
class ActivityUnavailable(ActivityEvent):
    pass


@dataclass
class ActivityTrigged(ActivityEvent):
    trigger: Selector  # who trigged the activity
    scene: Selector
