from __future__ import annotations

from dataclasses import dataclass

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from graia.ryanvk import ref

from .net.ws_client import SatoriWsClientNetworking
from .service import SatoriService


@dataclass
class SatoriConfig:
    host: URL | str
    port: int
    access_token: str | None = None

    def __post_init__(self):
        self.http_url = URL.build(scheme="http", host=str(self.host), port=self.port)
        self.ws_url = URL.build(scheme="ws", host=str(self.host), port=self.port)

def _import_performs():  # noqa: F401
    from avilla.satori.perform import context  # noqa: F401
    from avilla.satori.perform.action import message
    from avilla.satori.perform.event import message

_import_performs()

class SatoriProtocol(BaseProtocol):
    service: SatoriService

    artifacts = {
        **ref("avilla.protocol/satori::action"),
        **ref("avilla.protocol/satori::event"),
        **ref("avilla.protocol/satori::message"),
    }

    def __init__(self):
        self.service = SatoriService(self)


    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: SatoriConfig):
        self.service.connections.append(SatoriWsClientNetworking(self, config))
        return self
