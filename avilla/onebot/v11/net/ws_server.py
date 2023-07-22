from __future__ import annotations

from contextlib import suppress
import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from fastapi import FastAPI

from graia.amnesia.builtins.asgi import UvicornASGIService
from launart import Launchable
from launart.manager import Launart
from avilla.onebot.v11.net.base import OneBot11Networking

if TYPE_CHECKING:
    from avilla.onebot.v11.protocol import OneBot11Protocol


@dataclass
class OneBot11WsServerConfig:
    endpoint: str
    access_token: str | None = None


class OneBot11WsServerConnection(OneBot11Networking):
    ...

class OneBot11WsServerNetworking(Launchable):
    required: set[str] = set()
    stages: set[str] = {"preparing", "cleanup"}

    protocol: OneBot11Protocol
    config: OneBot11WsServerConfig

    def __init__(self, protocol: OneBot11Protocol) -> None:
        self.protocol = protocol
        super().__init__()

    async def websocket_server_handler(self):
        ...

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            asgi_service = manager.get_component("asgi.service/uvicorn")
            assert isinstance(asgi_service, UvicornASGIService)
            app = FastAPI()
            app.add_api_websocket_route("/onebot/v11/ws", self.websocket_server_handler)
            asgi_service.middleware.mounts[self.config.endpoint] = app  # type: ignore

        async with self.stage("cleanup"):
            with suppress(KeyError):
                del asgi_service.middleware.mounts[self.config.endpoint]
