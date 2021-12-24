from typing import TYPE_CHECKING

from uvicorn import Server
from uvicorn.config import Config

from avilla.core.launch import LaunchComponent
from avilla.core.service import Service
from avilla.core.service.common.http import ASGIHandlerProvider

if TYPE_CHECKING:
    from avilla.core import Avilla


class UvicornService(Service):
    supported_interface_types = set()
    supported_description_types = set()

    server: Server
    host: str
    port: int

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def get_interface(self, interface_type):
        pass

    def get_status(self, entity):
        raise NotImplementedError

    def set_status(self, entity, available: bool, description: str):
        raise NotImplementedError

    def set_current_status(self, available: bool, description: str):
        raise NotImplementedError

    async def launch_prepare(self, avilla: "Avilla"):
        asgi_handler = avilla.get_interface(ASGIHandlerProvider).get_asgi_handler()
        self.server = Server(Config(asgi_handler, host=self.host, port=self.port))

    async def launch_mainline(self, _):
        await self.server.serve()

    @property
    def launch_component(self) -> LaunchComponent:
        return LaunchComponent(
            "http.asgi_runner",
            {"http.universal_server"},
            self.launch_mainline,
            self.launch_prepare,
        )
