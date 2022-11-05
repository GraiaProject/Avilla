from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from typing_extensions import get_origin

from avilla.core.event import AvillaEvent
from avilla.core.resource import BlobResource, Resource
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core.account import AbstractAccount


@dataclass
class ResourceEvent(AvillaEvent):
    resource: Resource

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[ResourceEvent]"):
            if issubclass((get_origin(interface.annotation)) or interface.annotation, Resource):
                return interface.event.resource
            return await super().catch(interface)


class ResourceAvailable(ResourceEvent):
    pass


class ResourceUnavailable(ResourceEvent):
    pass


@dataclass
class FileUploaded(ResourceAvailable):
    uploader: Selector
    scene: Selector


@dataclass
class FileRemoved(ResourceUnavailable):
    uploader: Selector
    scene: Selector
