from __future__ import annotations

from typing import TYPE_CHECKING

from launart import Launart, Service
from loguru import logger

from avilla.spec.core.application import (
    ApplicationClosed,
    ApplicationClosing,
    ApplicationPreparing,
    ApplicationReady,
)

from .graia import AVILLA_ASCII_LOGO, AVILLA_ASCII_RAW_LOGO, log_telemetry

if TYPE_CHECKING:
    from .application import Avilla


class AvillaService(Service):
    id = "avilla.service"
    supported_interface_types = set()

    avilla: Avilla

    def __init__(self, avilla: Avilla):
        self.avilla = avilla
        super().__init__()

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    def get_interface(self, interface_type):
        ...

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            await self.avilla.broadcast.postEvent(ApplicationPreparing(self.avilla))

            logger.info(AVILLA_ASCII_RAW_LOGO, alt=AVILLA_ASCII_LOGO)
            log_telemetry()

            for protocol in self.avilla.protocols:
                logger.info(
                    f"Using platform: {protocol.__class__.platform}",
                    # alt=f"[magenta]Using platform: [/][dark_orange]{protocol.__class__.platform}[/]",
                )

        await self.avilla.broadcast.postEvent(ApplicationReady(self.avilla))

        async with self.stage("blocking"):
            ...  # TODO: 先放着.

        async with self.stage("cleanup"):
            await self.avilla.broadcast.postEvent(ApplicationClosing(self.avilla))

        await self.avilla.broadcast.postEvent(ApplicationClosed(self.avilla))
