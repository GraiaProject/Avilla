from __future__ import annotations

from inspect import isclass
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher

from avilla.core._runtime import cx_protocol
from avilla.core.account import BaseAccount
from avilla.core.context import Context
from avilla.core.event import AvillaEvent
from avilla.core.protocol import BaseProtocol

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core.application import Avilla


class AvillaBuiltinDispatcher(BaseDispatcher):
    avilla: Avilla

    def __init__(self, avilla: Avilla) -> None:
        self.avilla = avilla

    async def catch(self, interface: DispatcherInterface[AvillaEvent]):
        from avilla.core.application import Avilla

        if interface.annotation is Avilla:
            return self.avilla
        if interface.annotation in self.avilla._protocol_map:
            return self.avilla._protocol_map[interface.annotation]
        if (
            isclass(interface.annotation)
            and issubclass(interface.annotation, BaseProtocol)
            and isinstance(cx_protocol.get(None), interface.annotation)
        ):
            return cx_protocol.get(None)
        if (
            isinstance(interface.event, AvillaEvent)
            and isclass(interface.annotation)
            and issubclass(interface.annotation, BaseAccount)
        ):
            cx: Context = interface.local_storage["avilla_context"]
            return cx.account
