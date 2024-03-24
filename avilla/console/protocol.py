from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from avilla.core.utilles import cachedstatic
from flywheel import CollectContext

from .service import ConsoleService


class ConsoleProtocol(BaseProtocol):
    service: ConsoleService
    name: str

    @cachedstatic
    def artifacts():
        with CollectContext().collect_scope() as collect_context:
            # isort: off
            import avilla.console.perform.action.activity  # noqa
            import avilla.console.perform.action.message
            import avilla.console.perform.action.profile
            import avilla.console.perform.context
            import avilla.console.perform.event.message
            import avilla.console.perform.message.deserialize
            import avilla.console.perform.message.serialize  # noqa

        return collect_context

    def __init__(self, name: str = "robot"):
        self.name = name

    def ensure(self, avilla: Avilla):
        self.artifacts  # access at last 1 time.
        self.avilla = avilla
        self.service = ConsoleService(self)
        avilla.launch_manager.add_component(self.service)
