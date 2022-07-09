from __future__ import annotations

from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core import Avilla
    from avilla.core.event import AvillaEvent


class AvillaBuiltinDispatcher(BaseDispatcher):
    avilla: Avilla

    def __init__(self, avilla: Avilla) -> None:
        self.avilla = avilla

    async def catch(self, interface: DispatcherInterface[AvillaEvent]):
        if interface.annotation is Avilla:
            return self.avilla
        elif interface.annotation in self.avilla._protocol_map:
            return self.avilla._protocol_map[interface.annotation]
