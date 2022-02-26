from contextlib import asynccontextmanager
from typing import TYPE_CHECKING


from avilla.core.launch import LaunchComponent
from avilla.onebot.service import OnebotService

if TYPE_CHECKING:
    from .protocol import MiraigoProtocol

EllipsisType = type(...)


class MiraigoService(OnebotService):
    protocol: "MiraigoProtocol"

    def __init__(self, protocol: "MiraigoProtocol"):
        self.status = {}
        self.accounts = {}
        self.available_waiters = {}
        self.protocol = protocol

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent("avilla.miraigo.service", {"http.universal_client"}, self.launch_mainline)
