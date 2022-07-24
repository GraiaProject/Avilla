from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, MutableMapping
from weakref import WeakValueDictionary
from avilla.core.utilles.selector import Selector

from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.websocket import (
    AbstractWebsocketIO,
    WebsocketCloseEvent,
    WebsocketConnectEvent,
    WebsocketReceivedEvent,
    WebsocketReconnect,
)
from graia.amnesia.transport.common.websocket.shortcut import data_type, json_require
from graia.amnesia.transport.utilles import TransportRegistrar
from graia.amnesia.transport.common.http import AbstractClientInterface
from loguru import logger

from avilla.core.exceptions import RemoteError
from avilla.onebot.v12.account import OneBot12Account
from avilla.onebot.v12.connect import OneBot12Connection
from avilla.onebot.v12.connect.config import OneBot12WebsocketClientConfig
from avilla.onebot.v12.exception import get_error
from launart import Launart

if TYPE_CHECKING:
    from avilla.onebot.v12.protocol import OneBot12Protocol


registrar = TransportRegistrar()


@registrar.apply
class OneBot12WebsocketClientConnection(OneBot12Connection, Transport):
    id = "onebot.v12.connection.websocket.client"
    config: OneBot12WebsocketClientConfig

    io: AbstractWebsocketIO | None = None
    requests: MutableMapping[str, asyncio.Future]
    account: OneBot12Account | None = None 

    def __init__(self, protocol: OneBot12Protocol, config: OneBot12WebsocketClientConfig) -> None:
        super().__init__(protocol, config)
        self.requests = WeakValueDictionary()
        if config.account is not None:
            self.account = OneBot12Account(config.account, protocol)
            if protocol.avilla.get_account(selector=Selector().land(protocol.land).account(config.account)) is None:
                protocol.avilla.add_account(self.account)

    @property
    def stages(self):
        return {"blocking"}

    @property
    def required(self):
        return {"http.universal_client"}

    @registrar.on(WebsocketConnectEvent)
    async def on_connected(self, io: AbstractWebsocketIO) -> None:
        self.io = io
        self.status.connected = True

    @registrar.on(WebsocketCloseEvent)
    async def on_closed(self, io: AbstractWebsocketIO) -> None:
        self.status.connected = False

    @registrar.on(WebsocketReceivedEvent)
    @data_type(str)
    @json_require
    async def on_received(self, io: AbstractWebsocketIO, raw: Any) -> None:
        assert isinstance(raw, dict)
        if "echo" in raw:
            # action response: https://12.onebot.dev/connect/data-protocol/action-response/
            request = self.requests.get(raw["echo"])
            if request is not None:
                if raw["status"] != "ok":
                    error_type = get_error(raw["retcode"]) or RemoteError
                    error = error_type(raw["message"])
                    request.set_exception(error)
                request.set_result(raw["data"])
                return
            else:
                logger.warning("Received echo message, but no request found")
        # event: https://12.onebot.dev/connect/data-protocol/event/
        if self.config.account is None:
            self.config.account = raw["self_id"]
            self.account = OneBot12Account(self.config.account, self.protocol)
            self.protocol.avilla.add_account(self.account)
        if self.config.account is not None and raw["self_id"] != self.config.account:
            logger.warning(f'Received event from other account: {raw["self_id"]}, expected {self.config.account}', raw)
            return
        assert self.account is not None
        event = await self.protocol.event_parser.parse_event(self.protocol, self.account.to_selector(), raw)
        if event is not None:
            self.protocol.post_event(event)

    @registrar.on(WebsocketReconnect)
    async def on_reconnect(self, _):
        if self.account is None:
            logger.warning("Reconnecting for a client connection without account")
            await asyncio.sleep(3)
            logger.warning("Reconnecting websocket client which has no account")
        else:
            logger.warning(f"Websocket client for {self.account.id} disconnected, reconnecting...")
            await asyncio.sleep(5)
            logger.warning(f"Reconnecting websocket client for {self.account.id}")
        return True

    async def launch(self, manager: Launart):
        interface = manager.get_interface(AbstractClientInterface)
        if interface is None:
            raise RuntimeError("No http.universal_client interface found")
        