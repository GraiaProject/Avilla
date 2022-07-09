from __future__ import annotations

from typing import List

from graia.amnesia.launch import LaunchComponent, LaunchManager
from graia.amnesia.launch.service import Service
from loguru import logger


class IrcConnectionService(Service):
    supported_interface_types = set()

    connections: dict[str, _IrcProtocol]

    def __init__(self) -> None:
        self.connections = {}
    
    def get_interface(self, interface_type):
        ...

    async def launch_mainline(self, mgr: LaunchManager):
        ..

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            component_id="irc.service",
            required=set(),
            mainline=self.launch_mainline
        )
