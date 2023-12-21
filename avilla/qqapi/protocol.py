from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from graia.ryanvk import merge, ref

from .connection.ws_client import QQAPIWsClientNetworking
from .service import QQAPIService


@dataclass
class Intents:
    guilds: bool = True
    guild_members: bool = True
    guild_messages: bool = False
    """GUILD_MESSAGES"""
    guild_message_reactions: bool = True
    direct_message: bool = False
    """DIRECT_MESSAGES"""
    open_forum_event: bool = False
    audio_live_member: bool = False
    c2c_group_at_messages: bool = False
    interaction: bool = False
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
            | self.open_forum_event << 18
            | self.audio_live_member << 19
            | self.c2c_group_at_messages << 25
            | self.interaction << 26
            | self.message_audit << 27
            | self.forum_event << 28
            | self.audio_action << 29
            | self.at_messages << 30
        )

    @property
    def is_group_enabled(self) -> bool:
        """是否开启群聊功能"""
        return self.c2c_group_at_messages is True


@dataclass
class QQAPIConfig(ProtocolConfig):
    id: str
    token: str
    secret: str
    shard: tuple[int, int] | None = None
    intent: Intents = field(default_factory=Intents)
    is_sandbox: bool = False
    api_base: URL = URL("https://api.sgroup.qq.com/")
    sandbox_api_base: URL = URL("https://sandbox.api.sgroup.qq.com")
    auth_base: URL = URL("https://bots.qq.com/app/getAppAccessToken")

    def get_api_base(self) -> URL:
        return URL(self.sandbox_api_base) if self.is_sandbox else URL(self.api_base)

    @property
    def is_group_bot(self) -> bool:
        """是否为群机器人"""
        return self.intent.is_group_enabled


def _import_performs():  # noqa: F401
    # isort: off

    # :: Message
    import avilla.qqapi.perform.message.deserialize  # noqa: F401
    import avilla.qqapi.perform.message.serialize  # noqa: F401

    ## :: Action
    import avilla.qqapi.perform.action.user  # noqa: F401
    import avilla.qqapi.perform.action.channel  # noqa: F401
    import avilla.qqapi.perform.action.guild  # noqa: F401
    import avilla.qqapi.perform.action.guild_member  # noqa: F401
    import avilla.qqapi.perform.action.message  # noqa: F401
    import avilla.qqapi.perform.action.role  # noqa: F401

    ## :: Context
    import avilla.qqapi.perform.context  # noqa: F401

    ## :: Event
    import avilla.qqapi.perform.event.activity  # noqa: F401
    import avilla.qqapi.perform.event.audit  # noqa: F401
    import avilla.qqapi.perform.event.metadata  # noqa: F401
    import avilla.qqapi.perform.event.message  # noqa: F401
    import avilla.qqapi.perform.event.relationship  # noqa: F401

    ## :: Query
    import avilla.qqapi.perform.query  # noqa: F401

    ## :: Resource Fetch
    import avilla.qqapi.perform.resource_fetch  # noqa: F401


class QQAPIProtocol(BaseProtocol):
    service: QQAPIService

    def __init__(self):
        self.service = QQAPIService(self)

    _import_performs()
    artifacts = {
        **merge(
            ref("avilla.protocol/qqapi::context"),
            ref("avilla.protocol/qqapi::query"),
            ref("avilla.protocol/qqapi::resource_fetch"),
            ref("avilla.protocol/qqapi::action", "message"),
            ref("avilla.protocol/qqapi::action", "channel"),
            ref("avilla.protocol/qqapi::action", "guild"),
            ref("avilla.protocol/qqapi::action", "guild_member"),
            ref("avilla.protocol/qqapi::action", "role"),
            ref("avilla.protocol/qqapi::action", "user"),
            ref("avilla.protocol/qqapi::message", "deserialize"),
            ref("avilla.protocol/qqapi::message", "serialize"),
            ref("avilla.protocol/qqapi::event", "message"),
            ref("avilla.protocol/qqapi::event", "activity"),
            ref("avilla.protocol/qqapi::event", "relationship"),
            ref("avilla.protocol/qqapi::event", "metadata"),
            ref("avilla.protocol/qqapi::event", "audit"),
        ),
    }

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: QQAPIConfig):
        self.service.connections.append(QQAPIWsClientNetworking(self, config))
        return self
