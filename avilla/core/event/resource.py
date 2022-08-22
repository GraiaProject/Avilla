from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.event import AvillaEvent
from avilla.core.resource import BlobResource
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from avilla.core.account import AbstractAccount


class ResourceAvailable(AvillaEvent):
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


class ResourceUnavailable(AvillaEvent):
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
