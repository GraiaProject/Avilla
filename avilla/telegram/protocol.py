from __future__ import annotations

from dataclasses import dataclass

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from avilla.telegram.connection import TelegramLongPollingNetworking
from avilla.telegram.connection.webhook import TelegramWebhookNetworking
from avilla.telegram.service import TelegramService
from graia.ryanvk import merge, ref


@dataclass
class TelegramLongPollingConfig(ProtocolConfig):
    token: str
    base_url: URL = URL("https://api.telegram.org/")
    file_base_url: URL = URL("https://api.telegram.org/file/")
    timeout: int = 15
    proxy: str | None = None


@dataclass
class TelegramWebhookConfig(ProtocolConfig):
    token: str
    webhook_url: URL
    secret_token: str | None = None
    drop_pending_updates: bool = False
    base_url: URL = URL("https://api.telegram.org/")
    file_base_url: URL = URL("https://api.telegram.org/file/")
    proxy: str | None = None


def _import_performs():
    # isort: off

    # :: Action
    from .perform.action.chat import TelegramChatActionPerform  # noqa: F401
    from .perform.action.message import TelegramMessageActionPerform  # noqa: F401
    from .perform.action.preference import TelegramPreferenceActionPerform  # noqa: F401
    from .perform.action.reaction import TelegramReactionActionPerform  # noqa: F401
    from .perform.action.relation import TelegramRelationActionPerform  # noqa: F401

    # :: Event
    from .perform.event.message import TelegramEventMessagePerform  # noqa: F401

    # :: Message
    from .perform.message.deserialize import TelegramMessageDeserializePerform  # noqa: F401
    from .perform.message.serialize import TelegramMessageSerializePerform  # noqa: F401

    # :: Context
    from .perform.context import TelegramContextPerform  # noqa: F401

    # :: Resource Fetch
    from .perform.resource_fetch import TelegramResourceFetchPerform  # noqa: F401


class TelegramProtocol(BaseProtocol):
    service: TelegramService

    _import_performs()
    artifacts = {
        **merge(
            ref("avilla.protocol/telegram::action", "chat"),
            ref("avilla.protocol/telegram::action", "message"),
            ref("avilla.protocol/telegram::action", "preference"),
            ref("avilla.protocol/telegram::action", "reaction"),
            ref("avilla.protocol/telegram::action", "relation"),
            ref("avilla.protocol/telegram::event", "message"),
            ref("avilla.protocol/telegram::message", "deserialize"),
            ref("avilla.protocol/telegram::message", "serialize"),
            ref("avilla.protocol/telegram::context"),
            ref("avilla.protocol/telegram::resource_fetch"),
        ),
    }

    def __init__(self):
        self.service = TelegramService(self)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)

    def configure(self, config: TelegramLongPollingConfig | TelegramWebhookConfig):
        if isinstance(config, TelegramLongPollingConfig):
            connection = TelegramLongPollingNetworking(self, config)
        elif isinstance(config, TelegramWebhookConfig):
            connection = TelegramWebhookNetworking(self, config)
        else:
            raise ValueError("Invalid config type")
        self.service.connection_map[connection.account_id] = connection
        return self
