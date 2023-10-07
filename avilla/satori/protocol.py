from __future__ import annotations

from dataclasses import dataclass

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol

from .net.ws_client import SatoriWsClientNetworking
from .service import SatoriService


@dataclass
class SatoriConfig:
    endpoint: URL
    access_token: str | None = None



class SatoriProtocol(BaseProtocol):
    service: SatoriService

    def __init__(self):
        self.service = SatoriService(self)

    @classmethod
    def __init_isolate__(cls):
        # isort: off

        # :: Message
        from .perform.message.deserialize import SatoriMessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import SatoriMessageSerializePerform  # noqa: F401

        # :: Action
        from .perform.action.message import SatoriMessageActionPerform  # noqa: F401
        from .perform.action.admin import SatoriPrivilegeActionPerform  # noqa: F401
        from .perform.action.ban import SatoriBanActionPerform  # noqa: F401
        from .perform.action.leave import SatoriLeaveActionPerform  # noqa: F401
        from .perform.action.mute import SatoriMuteActionPerform  # noqa: F401

        # :: Context
        from .perform.context import SatoriContextPerform  # noqa: F401

        # :: Event
        from .perform.event.message import SatoriEventMessagePerform  # noqa: F401
        from .perform.event.lifespan import SatoriEventLifespanPerform  # noqa: F401

        # :: Resource Fetch
        from .perform.resource_fetch import SatoriResourceFetchPerform  # noqa: F401

        # :: Query
        from .perform.query.group import SatoriGroupQueryPerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: SatoriConfig):
        self.service.connections.append(SatoriWsClientNetworking(self, config))
        return self
