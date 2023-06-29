from __future__ import annotations

import asyncio
import hmac
from contextlib import suppress
from typing import TYPE_CHECKING, TypeVar

from graia.amnesia.json import Json
from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.client import AbstractClientInterface
from graia.amnesia.transport.common.http.extra import HttpRequest
from graia.amnesia.transport.common.server import AbstractRouter
from graia.amnesia.transport.common.websocket import (
    AbstractWebsocketIO,
    WebsocketCloseEvent,
    WebsocketConnectEvent,
    WebsocketEndpoint,
    WebsocketReceivedEvent,
    WebsocketReconnect,
)
from graia.amnesia.transport.common.websocket.shortcut import data_type, json_require
from graia.amnesia.transport.rider import TransportRider
from graia.amnesia.transport.utilles import TransportRegistrar
from launart import Launart
from loguru import logger

from avilla.core.event.lifecycle import AccountAvailable, AccountUnavailable
from avilla.core.exceptions import ActionFailed

from . import OneBot11Connection
from .config import OneBot11WebsocketClientConfig, OneBot11WebsocketServerConfig

if TYPE_CHECKING:
    from ..account import OneBot11Account

C = TypeVar("C", OneBot11WebsocketClientConfig, OneBot11WebsocketServerConfig)
I = TypeVar("I", AbstractClientInterface, AbstractRouter)

t = TransportRegistrar()


@t.apply
class OneBot11WebsocketConnection(OneBot11Connection[C, I], Transport):
    io: AbstractWebsocketIO

    _futures: dict[str, asyncio.Future[dict]]

    def __init__(self, account: OneBot11Account, config: C) -> None:
        super().__init__(account, config)
        self._futures = {}

    @t.on(WebsocketReceivedEvent)
    @data_type(str)
    @json_require  # type: ignore
    async def on_received(self, _, raw: dict) -> None:
        if echo := raw.get("echo"):
            if future := self._futures.get(echo):
                future.set_result(raw)
            return

        account = self.account
        protocol = account.protocol
        if event := await protocol.event_parser.parse_event(protocol, account, raw):
            with account._status_update():
                if isinstance(event, AccountAvailable):
                    self.status.connected = True
                elif isinstance(event, AccountUnavailable):
                    self.status.connected = False
                else:
                    protocol.post_event(event)

    @t.handle(WebsocketReconnect)
    async def on_reconnect(self, _) -> bool:
        logger.warning("Websocket reconnecting in 5s...", style="dark_orange")
        await asyncio.sleep(5)
        logger.warning("Websocket reconnecting...", style="dark_orange")
        return True

    @t.on(WebsocketCloseEvent)
    async def on_close(self, _) -> None:
        with self.account._status_update():
            self.status.connected = False
        logger.info("Websocket connection closed", style="dark_orange")

    async def call(self, action: str, params: dict | None = None) -> dict | None:
        future: asyncio.Future[dict] = asyncio.get_running_loop().create_future()
        echo = str(hash(future))
        self._futures[echo] = future

        try:
            await self.status.wait_for_available()
            await self.io.send(Json.serialize({"action": action, "params": params, "echo": echo}))
            result = await future
        finally:
            del self._futures[echo]

        if result["status"] != "ok":
            raise ActionFailed(f"{result['retcode']}: {result}")

        return result["data"]


t = TransportRegistrar()


@t.apply
class OneBot11WebsocketClientConnection(
    OneBot11WebsocketConnection[OneBot11WebsocketClientConfig, AbstractClientInterface]
):
    id = "onebot11.connection.websocket_client"
    required = {AbstractClientInterface}
    stages = {"blocking"}

    @t.on(WebsocketConnectEvent)
    async def on_connect(self, io: AbstractWebsocketIO):
        self.io = io

    async def launch(self, manager: Launart) -> None:
        self.interface = manager.get_interface(AbstractClientInterface)
        status = manager.status
        wait_for_sigexit = status.wait_for_sigexit()

        async with self.stage("blocking"):
            while not status.exiting:
                try:
                    rider: TransportRider = await self.interface.websocket(
                        str(self.config.host),
                        headers={"Authorization": f"Bearer {access_token}"}
                        if (access_token := self.config.access_token) is not None
                        else None,
                    )  # type: ignore
                    await asyncio.wait(
                        map(asyncio.ensure_future, (rider.use(self), wait_for_sigexit)),
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                except Exception as e:
                    logger.exception(e)
                    await asyncio.wait(
                        map(asyncio.ensure_future, (self.on_reconnect(self.status), wait_for_sigexit)),
                        return_when=asyncio.FIRST_COMPLETED,
                    )


t = TransportRegistrar()


@t.apply
class OneBot11WebsocketServerConnection(OneBot11WebsocketConnection[OneBot11WebsocketServerConfig, AbstractRouter]):
    id = "onebot11.connection.websocket_server"
    required = {AbstractRouter}
    stages = set()

    def __init__(self, account: OneBot11Account, config: OneBot11WebsocketServerConfig) -> None:
        super().__init__(account, config)
        self.declares.append(WebsocketEndpoint(config.host.path))

    @t.on(WebsocketConnectEvent)
    async def on_connect(self, io: AbstractWebsocketIO) -> None:
        with suppress(AttributeError):
            if not self.io.closed:
                return

        headers = (await io.extra(HttpRequest)).headers
        if headers.get("X-Self-ID") != self.account.id:
            return  # TODO: hot register
        await io.accept()
        if not (
            (access_token := self.config.access_token) is None
            or hmac.compare_digest(headers.get("Authorization", "Bearer ")[7:], access_token)
        ):
            return await io.close()
        elif headers.get("X-Client-Role") != "Universal":
            logger.warning("OneBot11Protocol only support Universal client", style="dark_orange")
            return await io.close()

        self.io = io

    async def launch(self, manager: Launart):
        self.interface = manager.get_interface(AbstractRouter)
        self.interface.use(self)
