from __future__ import annotations

from typing import TYPE_CHECKING

from launart import Launart, Service

from avilla.core.event.lifecycle import (
    ApplicationClosed,
    ApplicationClosing,
    ApplicationPreparing,
    ApplicationReady,
)

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

        self.avilla.broadcast.postEvent(ApplicationReady(self.avilla))

        async with self.stage("blocking"):
            ...  # TODO: 先放着.

        async with self.stage("cleanup"):
            self.avilla.broadcast.postEvent(ApplicationClosing(self.avilla))

        self.avilla.broadcast.postEvent(ApplicationClosed(self.avilla))
