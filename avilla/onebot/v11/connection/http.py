from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import cast

from graia.amnesia.json import Json
from graia.amnesia.transport.common.http import AbstractClientInterface
from graia.amnesia.transport.common.http.io import AbstractClientRequestIO
from graia.amnesia.transport.rider import TransportRider
from launart import Launart
from loguru import logger

from avilla.core.exceptions import ActionFailed
from avilla.onebot.v11.connection.config import OneBot11HttpClientConfig

from . import OneBot11Connection


class OneBot11HttpClientConnection(OneBot11Connection[OneBot11HttpClientConfig]):
    name = "http_client"
    required = {"http.universal_client"}
    stages = {"blocking"}

    client_interface: AbstractClientInterface

    async def call(self, action: str, params: dict | None = None) -> dict | None:
        rider: TransportRider = await self.client_interface.request(  # TODO: await Transport
            "POST",
            str(self.config.host / action),
            headers={"Authorization": f"Bearer {self.config.access_token}"},
            json=params,
        )  # type: ignore
        io: AbstractClientRequestIO = rider.io()
        data = (await io.read()).decode()
        result = Json.deserialize(data)

        assert isinstance(result, dict)
        if result["status"] != "ok":
            raise ActionFailed(f"{result['retcode']}: {result}")

        return cast(dict | None, result["data"])

    async def launch(self, manager: Launart) -> None:
        self.client_interface = manager.get_interface(AbstractClientInterface)
        status = manager.get_service("onebot11.service").status

        async with self.stage("blocking"):
            while not status.finished:
                try:
                    result = await self.call("get_status") or {}
                    assert result["online"] and result["good"]
                    self.status.connected = True
                except Exception as e:
                    self.status.connected = False
                    logger.exception(e)
                with suppress(TimeoutError):
                    await asyncio.wait_for(self.wait_for("finished", "onebot11.service"), 5)


class OneBot11HttpServerConnection(OneBot11Connection):
    pass
