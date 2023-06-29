from __future__ import annotations

import asyncio
import hmac
from contextlib import suppress
from typing import TYPE_CHECKING, NoReturn, cast

from loguru import logger

from avilla.core.exceptions import ActionFailed
from avilla.standard.core.application import AccountAvailable, AccountUnavailable
from graia.amnesia.json import Json
from graia.amnesia.transport import Transport
from graia.amnesia.transport.common.client import AbstractClientInterface
from graia.amnesia.transport.common.http import AbstractServerRequestIO, HttpEndpoint
from graia.amnesia.transport.common.http.io import AbstractClientRequestIO
from graia.amnesia.transport.common.server import AbstractRouter
from graia.amnesia.transport.rider import TransportRider
from launart import Launart

from . import OneBot11Connection
from .config import OneBot11HttpClientConfig, OneBot11HttpServerConfig

if TYPE_CHECKING:
    from ..account import OneBot11Account


class OneBot11HttpClientConnection(OneBot11Connection[OneBot11HttpClientConfig, AbstractClientInterface]):
    id = "onebot11.connection.http_client"
    required = {AbstractClientInterface}
    stages = {"blocking"}

    async def call(self, action: str, params: dict | None = None) -> dict | None:
        rider: TransportRider = await self.interface.request(
            "POST",
            str(self.config.host / action),
            headers={"Authorization": f"Bearer {access_token}"}
            if (access_token := self.config.access_token) is not None
            else None,
            json=params,
        )  # type: ignore
        io: AbstractClientRequestIO = rider.io()
        raw: dict = Json.deserialize((await io.read()).decode())  # type: ignore

        if raw["status"] != "ok":
            raise ActionFailed(f"{raw['retcode']}: {raw}")

        return cast(dict | None, raw["data"])

    async def launch(self, manager: Launart) -> None:
        wait_for_sigexit = manager.status.wait_for_sigexit()
        self.interface = manager.get_interface(AbstractClientInterface)

        async with self.stage("blocking"):
            while not manager.status.exiting:
                try:
                    result: dict = await self.call("get_status")  # type: ignore
                    with self.account._status_update():
                        self.status.connected = result["online"] and result["good"]
                except Exception as e:
                    with self.account._status_update():
                        self.status.connected = False
                    logger.exception(e)
                with suppress(TimeoutError):
                    await asyncio.wait_for(wait_for_sigexit, 5)


class OneBot11HttpServerConnection(OneBot11Connection[OneBot11HttpServerConfig, AbstractRouter], Transport):
    id = "onebot11.connection.http_server"
    required = {AbstractRouter}
    stages = set()

    def __init__(self, account: OneBot11Account, config: OneBot11HttpServerConfig) -> None:
        super().__init__(account, config)
        self.handlers[HttpEndpoint(config.host.path, ["POST"])] = type(self).handle_request

    async def handle_request(self, io: AbstractServerRequestIO):
        headers = await io.headers()
        raw = await io.read()

        if headers.get("X-Self-ID") != self.account.id:
            return  # TODO: hot register
        elif not (
            (access_token := self.config.access_token) is None
            or hmac.compare_digest(
                headers.get("X-Signature", "sha1=")[5:],
                hmac.new(access_token.encode(), raw, "sha1").hexdigest(),
            )
        ):
            return "Authorization failed", {"status": 401}

        account = self.account
        protocol = account.protocol
        if event := await protocol.event_parser.parse_event(protocol, account, Json.deserialize(raw.decode())):  # type: ignore
            with account._status_update():
                if isinstance(event, AccountAvailable):
                    self.status.connected = True
                elif isinstance(event, AccountUnavailable):
                    self.status.connected = False
                else:
                    protocol.post_event(event)

        return "", {"status": 204}

    async def call(self, action: str, params: dict | None = None) -> NoReturn:
        raise NotImplementedError

    async def launch(self, manager: Launart):
        self.interface = manager.get_interface(AbstractRouter)
        self.interface.use(self)
