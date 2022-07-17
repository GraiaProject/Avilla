from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Generic, MutableMapping, TypeVar
from weakref import WeakValueDictionary

import msgpack
from graia.amnesia.builtins.aiohttp import AiohttpClientInterface
from graia.amnesia.json.frontend import Json
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

from avilla.core.exceptions import RemoteError

from ..account import OneBot12Account
from ..connection import OneBot12Connection
from ..connection.config import (
    OneBot12Config,
    OneBot12WebsocketClientConfig,
    OneBot12WebsocketServerConfig,
)
from ..exceptions import get_error

if TYPE_CHECKING:
    from ..protocol import OneBot12Protocol


T_Config = TypeVar("T_Config", bound=OneBot12Config)


registrar = TransportRegistrar()


@registrar.apply
class OneBot12WebsocketConnection(OneBot12Connection, Transport, Generic[T_Config]):
    io: AbstractWebsocketIO | None = None
    requests: MutableMapping[str, asyncio.Future]
    confgi: T_Config

    def __init__(self, protocol: OneBot12Protocol, config: T_Config) -> None:
        super().__init__(protocol, config)
        self.requests = WeakValueDictionary()
        self.accounts = {}

    @registrar.on(WebsocketConnectEvent)
    async def on_connected(self, io: AbstractWebsocketIO) -> None:
        self.io = io
        self.status.connected = True

    @registrar.on(WebsocketCloseEvent)
    async def on_closed(self, io: AbstractWebsocketIO) -> None:
        self.status.connected = False

    @registrar.on(WebsocketReceivedEvent)
    async def on_received(self, io: AbstractWebsocketIO, raw: Any) -> None:
        raw = msgpack.loads(raw) if self.config.msgpack else Json.deserialize(raw)
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
            else:
                logger.warning("Received echo message, but no request found")
            return

        # event: https://12.onebot.dev/connect/data-protocol/event/
        if self.config.accounts is not None and raw["self_id"] not in self.config.accounts:
            if self.config.extra == "close":
                logger.warning(f"Received event from unknown account {raw['platform']}:{raw['self_id']}")
                logger.warning("close connection")
                await io.close()
                return
            elif self.config.extra == "warn":
                logger.warning(f"Received event from unknown account {raw['platform']}:{raw['self_id']}")
            elif self.config.extra == "allow":
                account = OneBot12Account(raw["self_id"], self.protocol, self.protocol.land)
                self.accounts[raw["self_id"]] = account
                self.protocol.avilla.add_account(account)

        event = await self.protocol.event_parser.parse_event(
            self.protocol, self.accounts[raw["self_id"]].to_selector(), raw
        )
        if event:
            self.protocol.post_event(event)


class OneBot12WebsocketClientConnection(OneBot12WebsocketConnection[OneBot12WebsocketClientConfig]):
    id = "onebot.v12.connection.websocket.client"

    @property
    def required(self):
        return {"http.universal_client"}


class OneBot12WebsocketServerConnection(OneBot12WebsocketConnection[OneBot12WebsocketServerConfig]):
    id = "onebot.v12.connection.websocket.server"

    @property
    def required(self):
        return {"http.universal_server"}
