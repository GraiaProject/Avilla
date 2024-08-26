from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, cast

from graia.amnesia.builtins.asgi import UvicornASGIService
from launart import Service
from launart.manager import Launart
from launart.utilles import any_completed
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket
from yarl import URL

from avilla.onebot.v11.net.base import OneBot11Networking
from avilla.standard.core.account import AccountUnregistered

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account
    from avilla.onebot.v11.protocol import OneBot11Protocol, OneBot11ReverseConfig


class OneBot11WsServerConnection(OneBot11Networking):
    connection: WebSocket

    def __init__(self, connection: WebSocket, protocol: OneBot11Protocol):
        self.connection = connection
        super().__init__(protocol)

    @property
    def id(self):
        return self.connection.headers["X-Self-ID"]

    @property
    def alive(self) -> bool:
        return not self.close_signal.is_set()

    async def message_receive(self):
        async for msg in self.connection.iter_json():
            yield self, msg
        else:
            await self.connection_closed()

    async def wait_for_available(self):
        return

    async def send(self, payload: dict) -> None:
        return await self.connection.send_json(payload)

    async def unregister_account(self):
        avilla = self.protocol.avilla
        for n in list(avilla.accounts.keys()):
            account = cast("OneBot11Account", avilla.accounts[n].account)
            account.status.enabled = False
            await avilla.broadcast.postEvent(AccountUnregistered(avilla, avilla.accounts[n].account))
            if n.follows("land(qq).account") and int(n["account"]) in self.accounts:
                del avilla.accounts[n]


class OneBot11WsServerNetworking(Service):
    required: set[str] = {"asgi.service/uvicorn"}
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    protocol: OneBot11Protocol
    config: OneBot11ReverseConfig

    connections: dict[str, OneBot11WsServerConnection]

    def __init__(self, protocol: OneBot11Protocol, config: OneBot11ReverseConfig) -> None:
        self.protocol = protocol
        self.config = config
        self.connections = {}
        super().__init__()

    @property
    def id(self):
        return f"onebot/v11/connection/websocket/server#{id(self)}"

    async def websocket_server_handler(self, ws: WebSocket):
        if ws.headers.get("Authorization", "")[7:] != (self.config.access_token or ""):
            return await ws.close()

        account_id = ws.headers["X-Self-ID"]

        await ws.accept()
        connection = OneBot11WsServerConnection(ws, self.protocol)
        self.connections[account_id] = connection

        try:
            await any_completed(connection.message_handle(), connection.close_signal.wait())
        finally:
            await connection.unregister_account()
            del self.connections[account_id]

    async def launch(self, manager: Launart):
        url = URL("/") / self.config.path / self.config.endpoint
        async with self.stage("preparing"):
            asgi_service = manager.get_component(UvicornASGIService)
            app = Starlette(routes=[WebSocketRoute(str(url), self.websocket_server_handler)])
            asgi_service.middleware.mounts[self.config.prefix.rstrip("/")] = app  # type: ignore

        async with self.stage("blocking"):
            await manager.status.wait_for_sigexit()

        async with self.stage("cleanup"):
            with suppress(KeyError):
                del asgi_service.middleware.mounts[self.config.endpoint]
