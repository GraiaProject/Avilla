from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from inspect import isclass
from typing import TYPE_CHECKING, Any, Literal

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from typing_extensions import Unpack

from avilla.core.account import BaseAccount
from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.selector import Selector

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

            if interface.name == "client" and interface.annotation is Selector:
                return interface.event.context.client

            if interface.name == "scene" and interface.annotation is Selector:
                return interface.event.context.scene

            if interface.name == "endpoint" and interface.annotation is Selector:
                return interface.event.context.endpoint

        @staticmethod
        async def afterExecution(interface: DispatcherInterface[AvillaEvent], exc, tb):
            if interface.depth < 1:
                cx_context.reset(interface.local_storage["_context_token"])
            await interface.event.context.staff.exit_stack.__aexit__(type(exc), exc, tb)


@dataclass
class RelationshipEvent(AvillaEvent):
    ...


@dataclass
class RelationshipCreated(RelationshipEvent):
    ...


@dataclass
class DirectSessionCreated(RelationshipCreated):
    ...


@dataclass
class SceneCreated(RelationshipCreated):
    ...


@dataclass
class MemberCreated(RelationshipEvent):
    ...


@dataclass
class RelationshipDestroyed(RelationshipEvent):
    active: bool
    indirect: bool = False


@dataclass
class DirectSessionDestroyed(RelationshipDestroyed):
    ...


@dataclass
class SceneDestroyed(RelationshipDestroyed):
    ...


@dataclass
class MemberDestroyed(RelationshipDestroyed):
    ...


@dataclass
class ModifyDetail:
    type: Literal["set", "clear", "update"]
    current: Any = None
    previous: Any = None

    def __repr__(self):
        return f"ModifyDetail({self.previous!r} -> {self.current!r})"


@dataclass
class MetadataModified(AvillaEvent):
    endpoint: Selector
    route: type[Metadata] | MetadataRoute[Unpack[tuple[Any, ...]], Metadata]
    details: dict[Any, ModifyDetail]
    operator: Selector | None = None
    scene: Selector | None = None

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface["MetadataModified"]):
            if interface.name == "details":
                if interface.annotation is dict:
                    return interface.event.details
                if interface.is_annotated and interface.annotated_origin is ModifyDetail:
                    return interface.event.details.get(interface.annotated_metadata[0])
            return await AvillaEvent.Dispatcher.catch(interface)
