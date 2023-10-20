from __future__ import annotations

from dataclasses import InitVar, dataclass, field

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from graia.ryanvk import ref, merge

from .net.ws_client import RedWsClientNetworking
from .service import RedService


@dataclass
class RedConfig(ProtocolConfig):
    access_token: str
    host: str = field(default="localhost")
    port: int = field(default=16530)
    _http_host: InitVar[str | None] = None
    endpoint: URL = field(init=False)
    http_endpoint: URL = field(init=False)

    def __post_init__(self, _http_host: str | None):
        if not self.access_token:
            raise ValueError("access_token must be set")
        self.endpoint = URL.build(scheme="ws", host=self.host, port=self.port)
        self.http_endpoint = URL.build(scheme="http", host=_http_host or self.host, port=self.port)

def _import_performs():  # noqa: F401
    # isort: off

    # :: Message
    import avilla.red.perform.message.deserialize  # noqa: F401
    import avilla.red.perform.message.serialize  # noqa: F401

    ## :: Action
    import avilla.red.perform.action.friend  # noqa: F401
    import avilla.red.perform.action.group  # noqa: F401
    import avilla.red.perform.action.member  # noqa: F401
    import avilla.red.perform.action.message  # noqa: F401

    ## :: Context
    import avilla.red.perform.context  # noqa: F401

    ## :: Event
    import avilla.red.perform.event.group  # noqa: F401
    import avilla.red.perform.event.member  # noqa: F401
    import avilla.red.perform.event.message  # noqa: F401
    import avilla.red.perform.event.lifespan  # noqa: F401
    import avilla.red.perform.event.relationship  # noqa: F401

    ## :: Query
    import avilla.red.perform.query  # noqa: F401

    ## :: Resource Fetch
    import avilla.red.perform.resource_fetch  # noqa: F401


class RedProtocol(BaseProtocol):
    service: RedService

    _import_performs()
    artifacts = {
        **merge(
            ref("avilla.protocol/red::context"),
            ref("avilla.protocol/red::query"),
            ref("avilla.protocol/red::resource_fetch"),
            ref("avilla.protocol/red::action", "message"),
            ref("avilla.protocol/red::action", "friend"),
            ref("avilla.protocol/red::action", "group"),
            ref("avilla.protocol/red::action", "member"),
            ref("avilla.protocol/red::message", "deserialize"),
            ref("avilla.protocol/red::message", "serialize"),
            ref("avilla.protocol/red::event", "message"),
            ref("avilla.protocol/red::event", "lifespan"),
            ref("avilla.protocol/red::event", "relationship"),
            ref("avilla.protocol/red::event", "group"),
            ref("avilla.protocol/red::event", "member")
        ),
    }

    def __init__(self):
        self.service = RedService(self)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: RedConfig):
        self.service.connections.append(RedWsClientNetworking(self, config))
        return self
