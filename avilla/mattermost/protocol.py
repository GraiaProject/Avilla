from __future__ import annotations

from dataclasses import dataclass

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig

from .connection.ws_client import MattermostWsClientNetworking
from .service import MattermostService


@dataclass
class MattermostConfig(ProtocolConfig):
    instance: str
    login_id: str
    password: str
    mfa_token: str | None = None


def _import_performs():  # noqa: F401
    ...


_import_performs()


class MattermostProtocol(BaseProtocol):
    service: MattermostService

    artifacts = {}

    def __init__(self):
        self.service = MattermostService(self)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: MattermostConfig):
        self.service.connections.append(MattermostWsClientNetworking(self, config))
        return self
