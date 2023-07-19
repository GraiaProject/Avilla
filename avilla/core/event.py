from __future__ import annotations

from abc import ABCMeta
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from typing_extensions import Unpack

from avilla.core.metadata import FieldReference, Metadata, MetadataRoute
from avilla.core.selector import Selector
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable

from ._runtime import cx_context

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from .context import Context


@dataclass
class AvillaEvent(Dispatchable, metaclass=ABCMeta):
    context: Context
    time: datetime = field(init=False, default_factory=datetime.now)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def beforeExecution(interface: DispatcherInterface[AvillaEvent]):
            interface.local_storage["avilla_context"] = interface.event.context
            interface.local_storage["_context_token"] = cx_context.set(interface.event.context)

        @staticmethod
        async def catch(interface: DispatcherInterface[AvillaEvent]):
            from .context import Context

            if interface.annotation is Context:
                return interface.event.context

        @staticmethod
        async def afterExecution(interface: DispatcherInterface[AvillaEvent], exc, tb):
            # FIXME: wait solution of GraiaProject/BroadcastControl#61
            with suppress(KeyError, RuntimeError):
                cx_context.reset(interface.local_storage["_context_token"])


@dataclass
class RelationshipCreated(AvillaEvent):
    ...

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["RelationshipCreated"]):
            return await super().catch(interface)


@dataclass
class RelationshipDestroyed(AvillaEvent):
    active: bool
    indirect: bool = False

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["RelationshipDestroyed"]):
            return await super().catch(interface)


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
        async def catch(interface: DispatcherInterface["RelationshipDestroyed"]):
            return await super().catch(interface)
