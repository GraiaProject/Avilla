from __future__ import annotations

from avilla.core.event import AvillaEvent
from avilla.core.utilles.selector import Selector


class ActivityAvailable(AvillaEvent):
    id: Selector  # eg. [...].activity("button_clicked")
    activity: Selector # eg. [...].button("#1")

    @property
    def ctx(self):
        return self.activity

class ActivityUnavailable(AvillaEvent):
    id: Selector
    activity: Selector

    @property
    def ctx(self):
        return self.activity

class ActivityTrigged(AvillaEvent):
    id: Selector
    activity: Selector

    trigger: Selector  # who trigged the activity
    mainline: Selector
    
    @property
    def ctx(self):
        return self.trigger