from __future__ import annotations

from dataclasses import dataclass

from avilla.core.event import AvillaEvent
from avilla.core.selector import Selector


@dataclass
class ActivityEvent(AvillaEvent):
    id: Selector  # eg. [...].activity("button_clicked")
    activity: Selector  # eg. [...].button("#1")


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
