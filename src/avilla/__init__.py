import asyncio
from typing import Dict, Generic, Type, TypeVar, Union

from graia.broadcast import Broadcast
from avilla.event import MessageChainDispatcher, RelationshipDispatcher

from avilla.network.client import Client
from avilla.network.interface import NetworkInterface
from avilla.network.service import Service
from avilla.protocol import BaseProtocol

T_Protocol = TypeVar("T_Protocol", bound=BaseProtocol)
T_Config = TypeVar("T_Config")


class Avilla(Generic[T_Protocol, T_Config]):
    broadcast: Broadcast
    protocol: T_Protocol
    network_interface: NetworkInterface
    configs: Dict[Type[T_Protocol], T_Config]

    def __init__(
        self,
        broadcast: Broadcast,
        protocol: Type[T_Protocol],
        networks: Dict[str, Union[Client, Service]],
        configs: Dict,
    ):
        self.broadcast = broadcast
        self.network_interface = NetworkInterface(networks)
        self.protocol = protocol(self, configs.get(protocol))
        self.configs = configs

        self.broadcast.dispatcher_interface.inject_global_raw(RelationshipDispatcher(), MessageChainDispatcher())

    async def launch(self):
        return await self.protocol.launch_entry()

    def launch_blocking(self):
        asyncio.get_event_loop().run_until_complete(self.launch())
