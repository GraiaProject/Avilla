from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .service import OneBot11Service


class OneBot11Protocol(BaseProtocol):
    service: OneBot11Service

    def __init__(self):
        self.service = OneBot11Service(self)

    @classmethod
    def __init_isolate__(cls):  # ruff: noqa: F401
        # isort: off

        # :: Message
        from .perform.message.deserialize import OneBot11MessageDeserializePerform
        from .perform.message.serialize import OneBot11MessageSerializePerform

        # :: Action
        from .perform.action.message import OneBot11MessageActionPerform

        # :: Event
        from .perform.event.message import OneBot11EventMessagePerform
        from .perform.event.lifespan import OneBot11EventLifespanPerform

        # :: Resource Fetch
        from .perform.resource_fetch import OneBot11ResourceFetchPerform

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
