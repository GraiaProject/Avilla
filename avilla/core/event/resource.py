from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from typing_extensions import get_origin

from avilla.core.event import AvillaEvent
from avilla.core.resource import BlobResource, Resource
from avilla.core.utilles.selector import Selector
from graia.broadcast.entities.dispatcher import BaseDispatcher

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface
    from avilla.core.account import AbstractAccount


class ResourceEvent(AvillaEvent):
    resource: BlobResource

    @property
    def ctx(self):
        return self.resource.selector

    def __init__(
            self,
            resource: BlobResource,
            account: AbstractAccount,
            time: datetime | None = None,
    ):
        self.resource = resource
        super().__init__(account, time=time)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: 'DispatcherInterface[ResourceEvent]'):
            if issubclass((get_origin(interface.annotation)) or interface.annotation, Resource):
                return interface.event.resource


class ResourceAvailable(ResourceEvent):
    pass


class ResourceUnavailable(ResourceEvent):
    pass


class FileUploaded(ResourceAvailable):
    uploader: Selector
    mainline: Selector

    def __init__(
        self,
        resource: BlobResource,
        uploader: Selector,
        mainline: Selector,
        account: AbstractAccount,
        time: datetime | None = None,
    ):
        self.uploader = uploader
        self.mainline = mainline
        super().__init__(resource, account, time)


class FileRemoved(ResourceUnavailable):
    uploader: Selector
    mainline: Selector

    def __init__(
        self,
        resource: BlobResource,
        uploader: Selector,
        mainline: Selector,
        account: AbstractAccount,
        time: datetime | None = None,
    ):
        self.uploader = uploader
        self.mainline = mainline
        super().__init__(resource, account, time)
