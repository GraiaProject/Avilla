import asyncio
from typing import Any, Optional, TYPE_CHECKING

from avilla.network.service import Service
from avilla.network.signatures import ServiceCommunicationMethod
from aiohttp import web

from avilla.utilles.transformer import OriginProvider

if TYPE_CHECKING:
    from avilla import Avilla

# TODO: aiohttp http server for service.


class AiohttpHttpServiceConfig(ServiceCommunicationMethod):
    host: str = "0.0.0.0"
    port: int = 8080

    def __init__(self, host: str = None, port: int = None):
        self.host = host or self.host
        self.port = port or self.port


class AiohttpHttpService(Service):
    app: web.Application

    def __init__(self, loop: asyncio.AbstractEventLoop, app: web.Application = None):
        self.app = app or web.Application(loop=loop)

    async def launchEntry(self, avilla: "Avilla", config: AiohttpHttpServiceConfig):
        loop = asyncio.get_running_loop()
        self.app.router

        server = loop.create_server(self.app.make_handler(), config.host, config.port)
        avilla.logger.info(f"Aiohttp service started on [{config.host}:{config.port}]")
