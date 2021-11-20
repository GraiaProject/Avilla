from typing import Any
from avilla.core.launch import LaunchComponent
from avilla.core.network.aiohttp.schema import ClientSchema
from avilla.core.network.service import Service, ServiceId
from aiohttp import ClientSession


class AiohttpClient(Service[ClientSchema, Any]):
    id = ServiceId("org.graia", "avilla.core", "http", "client")
    _aiohttp_session: ClientSession

    def __init__(self, session: ClientSession = None) -> None:
        self._aiohttp_session = session or ClientSession()

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            self.id.avilla_uri,
            set(),
            self.launch_mainline,
            self.launch_prepare,
            self.launch_cleanup,
        )

    async def launch_mainline(self):
        pass

    async def launch_cleanup(self):
        await self._aiohttp_session.close()
