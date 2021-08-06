from typing import Dict

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable


class HeartbeatReceived(Dispatchable):
    status: Dict
    interval: int

    def __init__(self, status: Dict, interval: int):
        self.status = status
        self.interval = interval

    def __repr__(self) -> str:
        return f"<HeartbeatReceived: status={self.status} interval={self.interval})>"

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface):
            return
