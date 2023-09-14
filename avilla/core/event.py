from __future__ import annotations

from inspect import isclass
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from typing_extensions import Unpack

from avilla.core.account import BaseAccount
from avilla.core.metadata import FieldReference, Metadata, MetadataRoute
from avilla.core.selector import Selector
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.entities.signatures import Force

from ._runtime import cx_context

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from .context import Context


@dataclass
class AvillaEvent(Dispatchable):
    context: Context
    time: datetime = field(init=False, default_factory=datetime.now)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def beforeExecution(interface: DispatcherInterface[AvillaEvent]):
            if interface.depth < 1:
                interface.local_storage["avilla_context"] = interface.event.context
                interface.local_storage["_context_token"] = cx_context.set(interface.event.context)
            await interface.event.context.staff.exit_stack.__aenter__()

        @staticmethod
        async def catch(interface: DispatcherInterface[AvillaEvent]):
            from .context import Context

            if interface.annotation is Context:
                return interface.event.context

            if isclass(interface.annotation) and issubclass(interface.annotation, BaseAccount):
                return interface.event.context.account

            if interface.name == "client":
                return interface.event.context.client

            if interface.name == "scene":
                return interface.event.context.scene

            if interface.name == "endpoint":
                return interface.event.context.endpoint

        @staticmethod
        async def afterExecution(interface: DispatcherInterface[AvillaEvent], exc, tb):
            if interface.depth < 1:
                cx_context.reset(interface.local_storage["_context_token"])
            await interface.event.context.staff.exit_stack.__aexit__(type(exc), exc, tb)


@dataclass
class RelationshipCreated(AvillaEvent):
    ...


@dataclass
class RelationshipDestroyed(AvillaEvent):
    active: bool
    indirect: bool = False


@dataclass
class ModifyDetail:
    type: Literal["set", "clear", "update"]
    current: Any = None
    previous: Any = None


@dataclass
class MetadataModified(AvillaEvent):
    endpoint: Selector
    route: type[Metadata] | MetadataRoute[Unpack[tuple[Any, ...]], Metadata]
    details: dict[FieldReference, ModifyDetail]
    operator: Selector | None = None
    scene: Selector | None = None

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MetadataModified"]):
            if interface.name == "route":
                return interface.event.route
            if interface.name == "details":
                return interface.event.details
            if interface.name == "operator":
                return Force(interface.event.operator)
            return await AvillaEvent.Dispatcher.catch(interface)
