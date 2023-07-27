from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .service import ConsoleService


class ConsoleProtocol(BaseProtocol):
    service: ConsoleService
    name: str

    def __init__(self, name: str = "robot"):
        self.name = name

    @classmethod
    def __init_isolate__(cls):  # ruff: noqa: F401
        # isort: off

        # :: Message
        from .perform.message.deserialize import ConsoleMessageDeserializePerform
        from .perform.message.serialize import ConsoleMessageSerializePerform

        # :: Action
        from .perform.action.message import ConsoleMessageActionPerform
        from .perform.action.activity import ConsoleActivityActionPerform
        from .perform.action.profile import ConsoleProfileActionPerform

        # :: Event
        from .perform.event.message import ConsoleEventMessagePerform

    def ensure(self, avilla: Avilla):
        self.avilla = avilla
        self.service = ConsoleService(self)
        avilla.launch_manager.add_component(self.service)
