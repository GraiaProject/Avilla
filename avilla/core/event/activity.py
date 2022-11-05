from __future__ import annotations
from dataclasses import dataclass

from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher

from avilla.core.event import AvillaEvent
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface


@dataclass
class ActivityEvent(AvillaEvent):
    id: Selector  # eg. [...].activity("button_clicked")
    activity: Selector  # eg. [...].button("#1")

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: 'DispatcherInterface[ActivityEvent]'):
            ...


class ActivityAvailable(ActivityEvent):
    pass


class ActivityUnavailable(ActivityEvent):
    pass


class ActivityTrigged(ActivityEvent):
    trigger: Selector  # who trigged the activity
    scene: Selector

