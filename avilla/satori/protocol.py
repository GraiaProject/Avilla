from __future__ import annotations

from satori.config import WebsocketsInfo
from satori.client.network.websocket import WsNetwork

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from graia.ryanvk import merge, ref

from .service import SatoriService


class SatoriConfig(ProtocolConfig, WebsocketsInfo):
    ...


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
    _import_performs()
    artifacts = {
        **merge(
            ref("avilla.protocol/satori::action", "message"),
            ref("avilla.protocol/satori::action", "request"),
            ref("avilla.protocol/satori::context"),
            ref("avilla.protocol/satori::resource_fetch"),
            ref("avilla.protocol/satori::message", "deserialize"),
            ref("avilla.protocol/satori::message", "serialize"),
            ref("avilla.protocol/satori::event", "message"),
            ref("avilla.protocol/satori::event", "lifespan"),
            ref("avilla.protocol/satori::event", "activity"),
            ref("avilla.protocol/satori::event", "metadata"),
            ref("avilla.protocol/satori::event", "relationship"),
            ref("avilla.protocol/satori::event", "request"),
        ),
    }

    def __init__(self):
        self.service = SatoriService(self)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: SatoriConfig):
        self.service.apply(config)
        return self
