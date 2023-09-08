from __future__ import annotations

from dataclasses import dataclass

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from avilla.telegram.service import TelegramService


@dataclass
class TelegramBotConfig:
    token: str
    base_url: URL = URL("https://api.telegram.org/bot")
    base_file_url: URL = URL("https://api.telegram.org/file/bot")
    timeout: int = 15


class TelegramProtocol(BaseProtocol):
    service: TelegramService

    def __init__(self):
        self.service = TelegramService(self)

    @classmethod
    def __init_isolate__(cls):
        # isort: off

        # :: Message
        from .perform.message.deserialize import TelegramMessageDeserializePerform  # noqa: F401
        from .perform.message.serialize import TelegramMessageSerializePerform  # noqa: F401

        # :: Event
        from .perform.event.message import TelegramEventMessagePerform  # noqa: F401

        # :: Action
        from .perform.action.message import TelegramMessageActionPerform  # noqa: F401

        # :: Resource Fetch
        from .perform.resource_fetch import TelegramResourceFetchPerform  # noqa: F401

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
