from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING
from avilla.core.metadata.model import Metadata

from graia.broadcast.entities.dispatcher import BaseDispatcher

from avilla.core.context import ctx_protocol, ctx_relationship
from avilla.core.relationship import Relationship

from avilla.core.event import AvillaEvent

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core import Avilla


class AvillaBuiltinDispatcher(BaseDispatcher):
    avilla: Avilla

    def __init__(self, avilla: Avilla) -> None:
        self.avilla = avilla

    async def catch(self, interface: DispatcherInterface[AvillaEvent]):
        from avilla.core import Avilla

        if interface.annotation is Avilla:
            return self.avilla
        elif interface.annotation in self.avilla._protocol_map:
            return self.avilla._protocol_map[interface.annotation]

class RelationshipDispatcher(BaseDispatcher):
    @staticmethod
    async def beforeExecution(interface: DispatcherInterface[AvillaEvent]):
        protocol = ctx_protocol.get()
        if protocol is not None:
            account = protocol.get_account(interface.event.account)
            if account is None:
                raise ValueError(f"Account {interface.event.account} not found")
            rs = await account.get_relationship(interface.event.ctx)
            token = ctx_relationship.set(rs)
            interface.local_storage["relationship"] = rs
            interface.local_storage["_ctxtoken_rs"] = token

    @staticmethod
    async def afterExecution(
        interface: DispatcherInterface[AvillaEvent],
        exception: Exception | None,
        tb: TracebackType | None,
    ):
        ctx_relationship.reset(interface.local_storage["_ctxtoken_rs"])

    @staticmethod
    async def catch(interface: DispatcherInterface[AvillaEvent]):
        if isinstance(interface.event, AvillaEvent):
            if interface.annotation is Relationship:
                return interface.local_storage["relationship"]

class MetadataDispatcher(BaseDispatcher):
    @staticmethod
    async def catch(interface: DispatcherInterface[AvillaEvent]):
        if isinstance(interface.event, AvillaEvent):
            if isinstance(interface.annotation, type) and issubclass(interface.annotation, Metadata):
                relationship: Relationship = interface.local_storage["relationship"]
                return await relationship.meta(interface.annotation)
