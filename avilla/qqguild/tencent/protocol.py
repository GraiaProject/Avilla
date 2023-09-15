from __future__ import annotations

from dataclasses import dataclass, field
from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from loguru import logger
from yarl import URL

from .service import QQGuildService
from .connection.ws_client import QQGuildWsClientNetworking

@dataclass
class Intents:
    guilds: bool = True
    guild_members: bool = True
    guild_messages: bool = False
    """GUILD_MESSAGES"""
    guild_message_reactions: bool = True
    direct_message: bool = False
    """DIRECT_MESSAGES"""
    message_audit: bool = True
    forum_event: bool = False
    audio_action: bool = False
    at_messages: bool = True
    """PUBLIC_GUILD_MESSAGES"""

    def __post_init__(self):
        if self.at_messages and self.guild_messages:
            logger.warning("at_messages and guild_messages are both enabled, which is not recommended.")

    def to_int(self) -> int:
        return (
            self.guilds << 0
            | self.guild_members << 1
            | self.guild_messages << 9
            | self.guild_message_reactions << 10
            | self.direct_message << 12
            | self.message_audit << 27
            | self.forum_event << 28
            | self.audio_action << 29
            | self.at_messages << 30
        )

@dataclass
class QQGuildConfig(ProtocolConfig):
    id: str
    token: str
    secret: str
    shard: tuple[int, int] | None = None
    intent: Intents = field(default_factory=Intents)
    is_sandbox: bool = False
    api_base: URL = URL("https://api.sgroup.qq.com/")
    sandbox_api_base: URL = URL("https://sandbox.api.sgroup.qq.com")

    def get_api_base(self) -> URL:
        return URL(self.sandbox_api_base) if self.is_sandbox else URL(self.api_base)

    def get_authorization(self) -> str:
        return f"Bot {self.id}.{self.token}"

class QQGuildProtocol(BaseProtocol):
    service: QQGuildService

    def __init__(self):
        self.service = QQGuildService(self)

    @classmethod
    def __init_isolate__(cls):
        ...
        # isort: off

        # :: Message
        from .perform.message.deserialize import QQGuildMessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import QQGuildMessageSerializePerform  # noqa: F401

        ## :: Action
        from .perform.action.channel import QQGuildChannelActionPerform  # noqa: F401
        from .perform.action.guild import QQGuildGuildActionPerform  # noqa: F401
        from .perform.action.member import QQGuildMemberActionPerform  # noqa: F401
        from .perform.action.message import QQGuildMessageActionPerform  # noqa: F401
        from .perform.action.role import QQGuildRoleActionPerform  # noqa: F401

        ## :: Context
        from .perform.context import QQGuildContextPerform   # noqa: F401

        ## :: Event
        from .perform.event.audit import QQGuildEventAuditPerform  # noqa: F401
        from .perform.event.message import QQGuildEventMessagePerform  # noqa: F401
        from .perform.event.metadata import QQGuildEventMetadataPerform  # noqa: F401
        from .perform.event.relationship import QQGuildEventRelationshipPerform  # noqa: F401

        ## :: Query
        from .perform.query import QQGuildQueryPerform  # noqa: F401

        ## :: Resource Fetch
        from .perform.resource_fetch import QQGuildResourceFetchPerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: QQGuildConfig):
        self.service.connections.append(
            QQGuildWsClientNetworking(self, config)
        )
        return self
