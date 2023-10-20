from __future__ import annotations


from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from graia.ryanvk import ref, merge
from satori.config import ClientInfo

from .service import SatoriService


class SatoriConfig(ProtocolConfig, ClientInfo):
    ...


def _import_performs():  # noqa: F401
    import avilla.satori.perform.context  # noqa: F401
    import avilla.satori.perform.resource_fetch  # noqa: F401
    import avilla.satori.perform.action.message
    import avilla.satori.perform.event.message
    import avilla.satori.perform.event.lifespan
    import avilla.satori.perform.message.deserialize
    import avilla.satori.perform.message.serialize  # noqa


class SatoriProtocol(BaseProtocol):
    service: SatoriService
    _import_performs()
    artifacts = {
        **merge(
            ref("avilla.protocol/satori::action", "message"),
            ref("avilla.protocol/satori::context"),
            ref("avilla.protocol/satori::resource_fetch"),
            ref("avilla.protocol/satori::message", "deserialize"),
            ref("avilla.protocol/satori::message", "serialize"),
            ref("avilla.protocol/satori::event", "message"),
            ref("avilla.protocol/satori::event", "lifespan"),
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
