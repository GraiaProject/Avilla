from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .service import OneBot11Service


class OneBot11Protocol(BaseProtocol):
    service: OneBot11Service

    def __init__(self):
        self.service = OneBot11Service(self)

    @classmethod
    def __init_isolate__(cls):
        # isort: off

        # :: Message
        from .perform.message.deserialize import OneBot11MessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import OneBot11MessageSerializePerform  # noqa: F401

        # :: Action
        from .perform.action.message import OneBot11MessageActionPerform  # noqa: F401
        from .perform.action.admin import OneBot11PrivilegeActionPerform  # noqa: F401
        from .perform.action.ban import OneBot11BanActionPerform  # noqa: F401
        from .perform.action.leave import OneBot11LeaveActionPerform  # noqa: F401
        from .perform.action.mute import OneBot11MuteActionPerform  # noqa: F401

        # :: Event
        from .perform.event.message import OneBot11EventMessagePerform  # noqa: F401
        from .perform.event.lifespan import OneBot11EventLifespanPerform  # noqa: F401

        # :: Resource Fetch
        from .perform.resource_fetch import OneBot11ResourceFetchPerform  # noqa: F401

        # :: Query
        from .perform.query.group import OneBot11GroupQueryPerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
