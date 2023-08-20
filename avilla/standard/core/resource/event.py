from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from typing_extensions import get_origin

from avilla.core.event import AvillaEvent
from avilla.core.resource import Resource
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface


@dataclass
class ResourceEvent(AvillaEvent):
    resource: Resource

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface[ResourceEvent]):
            if issubclass((get_origin(interface.annotation)) or interface.annotation, Resource):
                return interface.event.resource
            return await AvillaEvent.Dispatcher.catch(interface)


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
