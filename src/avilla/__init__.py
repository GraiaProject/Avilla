import asyncio
from typing import Dict, Generic, Type, TypeVar, Union

from graia.broadcast import Broadcast
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from avilla.builtins.profile import GroupProfile, MemberProfile
from avilla.event import MessageChainDispatcher, RelationshipDispatcher

from avilla.network.client import Client
from avilla.network.interface import NetworkInterface
from avilla.network.service import Service
from avilla.protocol import BaseProtocol
from avilla.relationship import Relationship

T_Protocol = TypeVar("T_Protocol", bound=BaseProtocol)
T_Config = TypeVar("T_Config")

MemberRelationship = Relationship[MemberProfile, None, T_Protocol]


class Avilla(Generic[T_Protocol, T_Config]):
    broadcast: Broadcast
    protocol: T_Protocol
    network_interface: NetworkInterface
    configs: Dict[Type[T_Protocol], T_Config]

    MemberRelationship = Relationship[MemberProfile, None, T_Protocol]
    GroupRelationship = Relationship[None, GroupProfile, T_Protocol]

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

        self.broadcast.dispatcher_interface.inject_global_raw(
            RelationshipDispatcher(), MessageChainDispatcher()
        )

        @self.broadcast.dispatcher_interface.inject_global_raw
        async def _(interface: DispatcherInterface):
            if interface.annotation is Avilla:
                return self
            elif interface.annotation is protocol:
                return self.protocol
            elif interface.annotation is NetworkInterface:
                return self.network_interface

    async def launch(self):
        return await self.protocol.launch_entry()

    def launch_blocking(self):
        asyncio.get_event_loop().run_until_complete(self.launch())
