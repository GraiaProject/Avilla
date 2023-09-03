from __future__ import annotations

from dataclasses import InitVar, dataclass, field

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from yarl import URL

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


class RedProtocol(BaseProtocol):
    service: RedService

    def __init__(self):
        self.service = RedService(self)

    @classmethod
    def __init_isolate__(cls):
        # isort: off

        # :: Message
        from .perform.message.deserialize import RedMessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import RedMessageSerializePerform  # noqa: F401

        ## :: Action
        from .perform.action.friend import RedFriendActionPerform  # noqa: F401
        from .perform.action.group import RedGroupActionPerform  # noqa: F401
        from .perform.action.member import RedMemberActionPerform  # noqa: F401
        from .perform.action.message import RedMessageActionPerform  # noqa: F401

        ## :: Context
        from .perform.context import RedContextPerform   # noqa: F401

        ## :: Event
        from .perform.event.group import RedEventGroupPerform  # noqa: F401
        from .perform.event.member import RedEventGroupMemberPerform  # noqa: F401
        from .perform.event.message import RedEventMessagePerform  # noqa: F401
        from .perform.event.lifespan import RedEventLifespanPerform  # noqa: F401
        from .perform.event.relationship import RedEventRelationshipPerform  # noqa: F401

        ## :: Query
        from .perform.query import RedQueryPerform  # noqa: F401

        ## :: Resource Fetch
        from .perform.resource_fetch import RedResourceFetchPerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: RedConfig):
        self.service.connections.append(
            RedWsClientNetworking(self, config)
        )
        return self
