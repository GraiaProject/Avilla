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
    def __init_isolate__(cls):
        # isort: off

        # :: Message
        from .perform.message.deserialize import ConsoleMessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import ConsoleMessageSerializePerform  # noqa: F401

        # :: Action
        from .perform.action.message import ConsoleMessageActionPerform  # noqa: F401
        from .perform.action.activity import ConsoleActivityActionPerform  # noqa: F401
        from .perform.action.profile import ConsoleProfileActionPerform  # noqa: F401

        # :: Event
        from .perform.event.message import ConsoleEventMessagePerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla
        self.service = ConsoleService(self)
        avilla.launch_manager.add_component(self.service)
