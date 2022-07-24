from __future__ import annotations

import asyncio
from typing import cast

from graia.amnesia.json import Json, TJson
from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.http import AbstractClientInterface
from graia.amnesia.transport.common.websocket import (
    AbstractWebsocketIO,
    WebsocketCloseEvent,
    WebsocketConnectEvent,
    WebsocketReceivedEvent,
    WebsocketReconnect,
)
from graia.amnesia.transport.common.websocket.shortcut import data_type, json_require
from graia.amnesia.transport.rider import TransportRider
from graia.amnesia.transport.utilles import TransportRegistrar
from launart import Launart
from loguru import logger

from avilla.core.exceptions import ActionFailed

from ..account import OneBot11Account
from . import OneBot11Connection
from .config import OneBot11WebsocketClientConfig

t = TransportRegistrar()


@t.apply
class OneBot11WebsocketClientConnection(OneBot11Connection[OneBot11WebsocketClientConfig], Transport):
    name = "websocket_client"
    required = {"http.universal_client"}
    stages = {"blocking"}

    client_interface: AbstractClientInterface
    websocket_io: AbstractWebsocketIO

    _futures: dict[str, asyncio.Future[dict]]

    def __init__(self, account: OneBot11Account, config: OneBot11WebsocketClientConfig) -> None:
        super().__init__(account, config)
        self._futures = {}

    @t.on(WebsocketConnectEvent)
    async def on_connect(self, websocket_io: AbstractWebsocketIO) -> None:
        self.websocket_io = websocket_io
        self.status.connected = True

    @t.handle(WebsocketReconnect)
    async def on_reconnect(self, _) -> bool:
        logger.warning("Websocket reconnecting in 5s...", style="dark_orange")
        await asyncio.sleep(5)
        logger.warning("Websocket reconnecting...", style="dark_orange")
        return True

    @t.on(WebsocketReceivedEvent)
    @data_type(str)
    @json_require
    async def on_received(self, _, data: TJson) -> None:
        assert isinstance(data, dict)

        if (echo := cast(str, data.get("echo"))) and (future := self._futures.get(echo)):
            return future.set_result(data)

        account = self.account
        protocol = account.protocol
        if event := await protocol.event_parser.parse_event(protocol, account.to_selector(), data):
            protocol.post_event(event)

    @t.on(WebsocketCloseEvent)
    async def on_close(self, _) -> None:
        self.status.connected = False
        logger.info("Websocket connection closed", style="dark_orange")

    async def call(self, action: str, params: dict | None = None) -> dict | None:
        future: asyncio.Future[dict] = asyncio.get_running_loop().create_future()
        echo = str(hash(future))
        self._futures[echo] = future

        await self.status.wait_for_available()
        await self.websocket_io.send(Json.serialize({"action": action, "params": params, "echo": echo}))
        try:
            result = await future
        finally:
            del self._futures[echo]

        if result["status"] != "ok":
            raise ActionFailed(f"{result['retcode']}: {result}")

        return cast(dict | None, result["data"])

    async def launch(self, manager: Launart) -> None:
        self.client_interface = manager.get_interface(AbstractClientInterface)

        async with self.stage("blocking"):
            rider: TransportRider = await self.client_interface.websocket(
                str(self.config.host),
                headers={"Authorization": f"Bearer {self.config.access_token}"},
            )  # type: ignore
            await asyncio.wait(
                map(asyncio.ensure_future, (rider.use(self), self.wait_for("finished", "onebot11.service"))),
                return_when=asyncio.FIRST_COMPLETED,
            )


class OneBot11WebsocketServerConnection(OneBot11Connection):
    pass
