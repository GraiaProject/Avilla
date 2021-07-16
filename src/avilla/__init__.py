import asyncio
from typing import Dict, Generic, Type, TypeVar

from graia.broadcast import Broadcast

T_Protocol = TypeVar("T_Protocol")
T_Config = TypeVar("T_Config")


class Avilla(Generic[T_Protocol, T_Config]):
    broadcast: Broadcast
    protocol: T_Protocol
    configs: Dict[Type[T_Protocol], T_Config]

    # TODO: network layer.

    def __init__(self, broadcast: Broadcast, protocol: Type[T_Protocol], configs: Dict):
        self.broadcast = broadcast
        self.protocol = protocol(self, configs.get(protocol.__class__))
        self.configs = configs

    async def launch(self):
        pass

    def launch_blocking(self):
        asyncio.get_event_loop().run_until_complete(self.launch())
