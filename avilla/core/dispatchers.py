from __future__ import annotations

from inspect import isclass
from types import TracebackType
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher

from avilla.core.account import AbstractAccount
from avilla.core._runtime import ctx_context, ctx_protocol
from avilla.core.event import AvillaEvent
from avilla.core.context import Context

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
        elif interface.annotation in self.avilla._protocol_map:
            return self.avilla._protocol_map[interface.annotation]
        elif isinstance(interface.event, AvillaEvent):
            if isclass(interface.annotation) and issubclass(interface.annotation, AbstractAccount):
                rs: Context = interface.local_storage["relationship"]
                return rs.account


"""
class MetadataDispatcher(BaseDispatcher):
    @staticmethod
    async def catch(interface: DispatcherInterface[AvillaEvent]):
        if isinstance(interface.event, AvillaEvent):
            if isinstance(interface.annotation, type) and issubclass(interface.annotation, Cell):
                relationship: Relationship = interface.local_storage["relationship"]
                return await relationship.meta(interface.annotation)
"""
