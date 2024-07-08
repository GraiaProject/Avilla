from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from aiohttp import ClientSession
from graia.amnesia.builtins.asgi import UvicornASGIService
from launart import Launart, Service, any_completed
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from avilla.standard.telegram.preference.capability import PreferenceCapability
from avilla.telegram.connection.base import TelegramNetworking

if TYPE_CHECKING:
    from avilla.telegram.protocol import TelegramProtocol, TelegramWebhookConfig


class TelegramWebhookNetworking(TelegramNetworking, Service):
    required: set[str] = {"asgi.service/uvicorn"}
    stages: set[str] = {"preparing", "blocking", "cleanup"}

    protocol: TelegramProtocol
    config: TelegramWebhookConfig

    __alive: bool
    __offset: int | None
    __queue: asyncio.Queue

    def __init__(self, protocol: TelegramProtocol, config: TelegramWebhookConfig):
        super().__init__(protocol)
        self.protocol = protocol
        self.config = config

    @property
    def alive(self) -> bool:
        return self.__alive

    @property
    def id(self):
        return f"telegram/connection/poll#{self.account_id}"

    @property
    def endpoint(self):
        return self.config.webhook_url.path

    async def message_receive(self):
        while not self.manager.status.exiting:
            data = await self.__queue.get()
            yield self, data

    async def wait_for_available(self):
        await self.status.wait_for_available()

    def get_staff_components(self):
        return {"connection": self, "protocol": self.protocol, "avilla": self.protocol.avilla, "account": self.account}

    def __staff_generic__(self, element_type: dict, event_type: dict):
        ...

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    async def request_handler(self, req: Request):
        if req.headers["X-Telegram-Bot-Api-Secret-Token"] != self.config.secret_token:
            return Response(status_code=401)

        data = await req.json()
        await self.__queue.put(data)
        return Response(status_code=204)

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.session = ClientSession()
            self.__offset = None
            self.__queue = asyncio.Queue()
            self.register()
            await self.staff.call_fn(
                PreferenceCapability.delete_webhook, drop_pending_updates=self.config.drop_pending_updates
            )

            asgi_service = manager.get_component(UvicornASGIService)
            app = Starlette(routes=[Route("/", self.request_handler, methods=["POST"])])
            asgi_service.middleware.mounts[self.endpoint.rstrip("/")] = app  # type: ignore
            await self.staff.call_fn(
                PreferenceCapability.set_webhook,
                url=str(self.config.webhook_url),
                secret_token=self.config.secret_token,
            )
            self.__alive = True

        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit(), self.daemon())

        async with self.stage("cleanup"):
            await self.staff.call_fn(PreferenceCapability.delete_webhook)
