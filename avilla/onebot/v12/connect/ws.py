from __future__ import annotations
import asyncio

from typing import TYPE_CHECKING, Any, MutableMapping
from weakref import WeakValueDictionary
from avilla.core.exceptions import RemoteError
from avilla.onebot.v12.account import OneBot12Account
from avilla.onebot.v12.connect import OneBot12Connection
from avilla.onebot.v12.connect.config import OneBot12WebsocketClientConfig
from avilla.onebot.v12.exception import get_error
from graia.amnesia.builtins.aiohttp import AiohttpClientInterface
from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.http.extra import HttpRequest
from graia.amnesia.transport.common.websocket import (
    AbstractWebsocketIO,
    WebsocketCloseEvent,
    WebsocketConnectEvent,
    WebsocketEndpoint,
    WebsocketReceivedEvent,
    WebsocketReconnect,
    WSConnectionAccept,
    WSConnectionClose,
)
from graia.amnesia.transport.common.websocket.shortcut import data_type, json_require
from graia.amnesia.transport.utilles import TransportRegistrar
from loguru import logger
if TYPE_CHECKING:
    from avilla.onebot.v12.protocol import OneBot12Protocol


registrar = TransportRegistrar()

@registrar.apply
class OneBot12WebsocketClientConnection(OneBot12Connection, Transport):
    id = "onebot.v12.connection.websocket.client"
    config: OneBot12WebsocketClientConfig

    io: AbstractWebsocketIO | None = None
    requests: MutableMapping[str, asyncio.Future]
    accounts: list[OneBot12Account]

    def __init__(self, protocol: OneBot12Protocol, config: OneBot12WebsocketClientConfig) -> None:
        super().__init__(protocol, config)
        self.requests = WeakValueDictionary()
        self.accounts = []

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
                    error_type = get_error(raw['retcode']) or RemoteError
                    error = error_type(raw['message'])
                    request.set_exception(error)
                request.set_result(raw['data'])
                return
            else:
                logger.warning("Received echo message, but no request found")
        # event: https://12.onebot.dev/connect/data-protocol/event/
        if self.config.accounts is not None and raw['self_id'] not in self.config.accounts:
            if self.config.extra == "close":
                logger.warning(f"Received event from unknown account {raw['platform']}:{raw['self_id']}")
                logger.warning("close connection")
                await io.close()
                return
            elif self.config.extra == "warn":
                logger.warning(f"Received event from unknown account {raw['platform']}:{raw['self_id']}")
            elif self.config.extra == "allow":
                account = OneBot12Account(raw['self_id'], self.protocol.land, self.protocol)
                self.accounts.append(account)
                self.protocol.avilla.add_account(account)
                ...
