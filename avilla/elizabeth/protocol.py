from __future__ import annotations

from dataclasses import dataclass, field
from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from yarl import URL

from .service import ElizabethService
from .connection.ws_client import ElizabethWsClientNetworking

@dataclass
class ElizabethConfig(ProtocolConfig):
    qq: int
    host: str
    port: int
    access_token: str
    base_url: URL = field(init=False)

    def __post_init__(self):
        self.base_url = URL.build(scheme="http", host=self.host, port=self.port)


class ElizabethProtocol(BaseProtocol):
    service: ElizabethService

    def __init__(self):
        self.service = ElizabethService(self)

    @classmethod
    def __init_isolate__(cls):
        ## :: Action
        from .perform.action.activity import ElizabethActivityActionPerform  # noqa: F401
        from .perform.action.announcement import ElizabethAnnouncementActionPerform  # noqa: F401
        from .perform.action.contact import ElizabethContactActionPerform  # noqa: F401
        from .perform.action.friend import ElizabethFriendActionPerform  # noqa: F401
        from .perform.action.group import ElizabethGroupActionPerform  # noqa: F401
        from .perform.action.group_member import ElizabethGroupMemberActionPerform  # noqa: F401
        from .perform.action.message import ElizabethMessageActionPerform  # noqa: F401
        from .perform.action.request import ElizabethRequestActionPerform  # noqa: F401

        ## ::Context
        from .perform.context import ElizabethContextPerform  # noqa: F401

        ## :: Event
        from .perform.event.activity import ElizabethEventActivityPerform  # noqa: F401
        from .perform.event.friend import ElizabethEventFriendPerform  # noqa: F401
        from .perform.event.group import ElizabethEventGroupPerform  # noqa: F401
        from .perform.event.group_member import ElizabethEventGroupMemberPerform  # noqa: F401
        from .perform.event.message import ElizabethEventMessagePerform  # noqa: F401
        from .perform.event.relationship import ElizabethEventRelationshipPerform  # noqa: F401
        from .perform.event.request import ElizabethEventRequestPerform  # noqa: F401

        ## :: Message
        from .perform.message.deserialize import ElizabethMessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import ElizabethMessageSerializePerform  # noqa: F401

        ## :: Query
        from .perform.query.announcement import ElizabethAnnouncementQueryPerform  # noqa: F401
        from .perform.query.bot import ElizabethBotQueryPerform  # noqa: F401
        from .perform.query.friend import ElizabethFriendQueryPerform  # noqa: F401
        from .perform.query.group import ElizabethGroupQueryPerform  # noqa: F401

        ## :: Resource Fetch
        from .perform.resource_fetch import ElizabethResourceFetchPerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: ElizabethConfig):
        self.service.connections.append(
            ElizabethWsClientNetworking(self, config)
        )
        return self
