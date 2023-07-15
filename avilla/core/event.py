from __future__ import annotations

from abc import ABCMeta
from contextlib import suppress
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from avilla.core._vendor.dataclasses import dataclass, field
from avilla.core.metadata import MetadataRoute
from avilla.core.ryanvk import Fn
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable

from ._runtime import cx_context

if TYPE_CHECKING:
    from avilla.core.metadata import MetadataFieldReference
    from avilla.core.selector import Selector
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
class Op:
    operator: Fn
    effects: dict[tuple[Selector, MetadataRoute], list[Effect]]


@dataclass
class NamelessOp:
    effects: dict[tuple[Selector, MetadataRoute], list[Effect]]


T = TypeVar("T")


@dataclass
class Effect(Generic[T]):
    field: MetadataFieldReference[Any, T]


@dataclass
class Bind(Effect[T]):
    value: T


@dataclass
class Unbind(Effect):
    ...


@dataclass
class Update(Effect[T]):
    present: T
    past: T | None = None


# TODO: Metadata Effect 原语补充


@dataclass
class MetadataModified(AvillaEvent):
    endpoint: Selector
    modifies: list[Op | NamelessOp]
    client: Selector | None = None
    scene: Selector | None = None

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MetadataModified"]):
            return await super().catch(interface)


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
