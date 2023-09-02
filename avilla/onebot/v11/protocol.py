from __future__ import annotations

from dataclasses import dataclass

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from yarl import URL

from .service import OneBot11Service
from .net.ws_client import OneBot11WsClientNetworking
from .net.ws_server import OneBot11WsServerNetworking


@dataclass
class OneBot11ForwardConfig:
    endpoint: URL
    access_token: str | None = None

@dataclass
class OneBot11ReverseConfig:
    endpoint: str
    access_token: str | None = None



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

        # :: Context
        from .perform.context import OneBot11ContextPerform  # noqa: F401

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

    def configure(self, config: OneBot11ForwardConfig | OneBot11ReverseConfig):
        if isinstance(config, OneBot11ForwardConfig):
            self.service.connections.append(OneBot11WsClientNetworking(self, config))
        elif isinstance(config, OneBot11ReverseConfig):
            self.service.connections.append(OneBot11WsServerNetworking(self, config))
        else:
            raise TypeError("Invalid config type")
        return self
