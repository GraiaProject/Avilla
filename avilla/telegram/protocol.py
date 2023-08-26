from __future__ import annotations

from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from avilla.telegram.service import TelegramService


class TelegramProtocol(BaseProtocol):
    service: TelegramService

    def __init__(self):
        self.service = TelegramService(self)

    @classmethod
    def __init_isolate__(cls):
        ...

    def ensure(self, avilla: Avilla):
        self.avilla = avilla

        avilla.launch_manager.add_component(self.service)
