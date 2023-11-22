from __future__ import annotations

from dataclasses import dataclass

from yarl import URL

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol, ProtocolConfig
from avilla.telegram.bot import TelegramBot
from avilla.telegram.service import TelegramService
from graia.ryanvk import merge, ref


@dataclass
class TelegramBotConfig(ProtocolConfig):
    token: str
    base_url: URL = URL("https://api.telegram.org/bot")
    base_file_url: URL = URL("https://api.telegram.org/file/bot")
    timeout: int = 15
    reformat: bool = False


def _import_performs():
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


class TelegramProtocol(BaseProtocol):
    service: TelegramService

    _import_performs()
    artifacts = {
        **merge(
            ref("avilla.protocol/telegram::resource_fetch"),
            ref("avilla.protocol/telegram::action", "message"),
            ref("avilla.protocol/telegram::action", "friend"),
            ref("avilla.protocol/telegram::action", "group"),
            ref("avilla.protocol/telegram::action", "member"),
            ref("avilla.protocol/telegram::message", "deserialize"),
            ref("avilla.protocol/telegram::message", "serialize"),
            ref("avilla.protocol/telegram::event", "message"),
            ref("avilla.protocol/telegram::event", "lifespan"),
            ref("avilla.protocol/telegram::event", "relationship"),
            ref("avilla.protocol/telegram::event", "group"),
            ref("avilla.protocol/telegram::event", "member"),
        ),
    }

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

    def configure(self, config: TelegramBotConfig):
        bot = TelegramBot(self, config)
        self.service.instance_map[bot.account_id] = bot
        return self
