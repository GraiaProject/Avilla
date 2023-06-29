from __future__ import annotations

from avilla.core.application import Avilla

from avilla.core.protocol import BaseProtocol

class OneBot11Protocol(BaseProtocol):
    

    @classmethod
    def __init_isolate__(cls):
        ...
    
    def ensure(self, avilla: Avilla):
        ...