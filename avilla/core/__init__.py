import asyncio
from logging import Logger, getLogger
from typing import Dict, Generic, List, Type, Union

from avilla.core.builtins.middlewares import target_context_injector
from avilla.core.event import MessageChainDispatcher, RelationshipDispatcher
from avilla.core.network.client import Client
from avilla.core.network.interface import NetworkInterface
from avilla.core.network.service import Service
from avilla.core.protocol import BaseProtocol
from avilla.core.typing import T_Config, T_ExecMW, T_Protocol
from graia.broadcast import Broadcast
from graia.broadcast.interfaces.dispatcher import DispatcherInterface


class Avilla(Generic[T_Protocol, T_Config]):
    broadcast: Broadcast
    protocol: T_Protocol
    network_interface: NetworkInterface
    configs: Dict[Type[T_Protocol], T_Config]
    middlewares: List[T_ExecMW]
    logger: Logger

    def __init__(
        self,
        broadcast: Broadcast,
        protocol: Type[T_Protocol],
        networks: Dict[str, Union[Client, Service]],
        configs: Dict,
        logger: Logger = None,
        middlewares: List[T_ExecMW] = None,
    ):
        self.broadcast = broadcast
        self.network_interface = NetworkInterface(networks)
        self.protocol = protocol(self, configs.get(protocol))
        self.configs = configs
        self.logger = logger or getLogger(__name__)
        self.middlewares = [target_context_injector, *(middlewares or [])]

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
        self.logger.info("hello, world!")
        if self.protocol.__class__.platform is not BaseProtocol.platform:
            self.logger.info(
                f"using platform: {self.protocol.__class__.platform.universal_identifier}"
            )
        return await self.protocol.launch_entry()

    def launch_blocking(self):
        asyncio.get_event_loop().run_until_complete(self.launch())
