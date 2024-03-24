from __future__ import annotations

from flywheel import CollectContext
from satori.config import WebsocketsInfo
from satori.client.network.websocket import WsNetwork

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from avilla.core.utilles import cachedstatic

from .service import SatoriService


class SatoriConfig(ProtocolConfig, WebsocketsInfo): ...


SatoriService.register_config(SatoriConfig, WsNetwork)


def _import_performs():
    import avilla.satori.perform.action.message  # noqa: F401
    import avilla.satori.perform.action.request  # noqa: F401
    import avilla.satori.perform.context  # noqa: F401
    import avilla.satori.perform.event.activity
    import avilla.satori.perform.event.lifespan
    import avilla.satori.perform.event.message
    import avilla.satori.perform.event.metadata
    import avilla.satori.perform.event.relationship
    import avilla.satori.perform.event.request
    import avilla.satori.perform.message.deserialize
    import avilla.satori.perform.message.serialize  # noqa
    import avilla.satori.perform.resource_fetch  # noqa: F401


class SatoriProtocol(BaseProtocol):
    service: SatoriService

    @cachedstatic
    def artifacts():
        with CollectContext().collect_scope() as collect_context:
            _import_performs()

        return collect_context

    def __init__(self):
        self.service = SatoriService(self)

    def ensure(self, avilla: Avilla):
        self.artifacts  # access at last 1 time.
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: SatoriConfig):
        self.service.apply(config)
        return self
