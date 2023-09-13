from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from graia.ryanvk import merge, ref

from .service import ConsoleService


def import_perform():
    # isort: off

    import avilla.console.perform.action.activity  # noqa
    import avilla.console.perform.action.message
    import avilla.console.perform.action.profile
    import avilla.console.perform.context
    import avilla.console.perform.event.message
    import avilla.console.perform.message.deserialize
    import avilla.console.perform.message.serialize  # noqa


class ConsoleProtocol(BaseProtocol):
    service: ConsoleService
    name: str
    import_perform()
    artifacts = {
        **merge(
            ref("avilla.protocol/console::action/activity"),
            ref("avilla.protocol/console::action/message"),
            ref("avilla.protocol/console::action/profile"),
            ref("avilla.protocol/console::action/get_context"),
            ref("avilla.protocol/console::message", "deserialize"),
            ref("avilla.protocol/console::message", "serialize"),
            ref("avilla.protocol/console::event/message"),
        ),
    }

    def __init__(self, name: str = "robot"):
        self.name = name

    def ensure(self, avilla: Avilla):
        self.avilla = avilla
        self.service = ConsoleService(self)
        avilla.launch_manager.add_component(self.service)
