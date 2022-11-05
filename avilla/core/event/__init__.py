from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, get_args, get_origin

from ..context import Context

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface
    from avilla.core.utilles.selector import Selector

    from .._runtime import ctx_avilla, ctx_context, ctx_protocol
    from ..metadata import MetadataOf

@dataclass
class AvillaEvent(Dispatchable, metaclass=ABCMeta):
    context: Context
    time: datetime = field(init=False, default_factory=datetime.now)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def beforeExecution(interface: DispatcherInterface[AvillaEvent]):
            interface.local_storage["avilla_context"] = interface.event.context
            interface.local_storage["_context_token"] = ctx_context.set(interface.event.context)
            # TODO: 重新评估此处: 由于 asyncio 会自动 copy_context, 所以在此 set ctxvar 的可用性存疑.
        
        @staticmethod
        async def afterExecution(interface: DispatcherInterface[AvillaEvent]):
            ctx_context.reset(interface.local_storage["_context_token"])

@dataclass
class MetadataModify:
    bound: Selector | MetadataOf
    field: str
    action: str
    past: Any
    present: Any

@dataclass
class MetadataModified(AvillaEvent):
    endpoint: Selector
    modifies: list[MetadataModify]
    operator: Selector | None = None

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MetadataModified"]):
            ...

@dataclass
class RelationshipCreated(AvillaEvent):
    client: Selector
    scene: Selector
    self: Selector
    mediums: list[Selector] = field(default_factory=list)

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["RelationshipCreated"]):
            ...

@dataclass
class RelationshipDestroyed(AvillaEvent):
    client: Selector
    scene: Selector
    self: Selector
    mediums: list[Selector] = field(default_factory=list)

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["RelationshipDestroyed"]):
            ...
