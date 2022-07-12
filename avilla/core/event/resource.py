from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from avilla.core.event import AvillaEvent
from avilla.core.resource import Resource
from avilla.core.utilles.selector import Selector

R = TypeVar("R", bound=Resource)


class ResourceAvailable(AvillaEvent, Generic[R]):
    resource: R

    @property
    def ctx(self):
        return self.resource.to_selector().set_referent(self.resource)

    @property
    def mainline(self):
        return self.resource.mainline

    def __init__(
        self,
        resource: R,
        account: Selector,
        time: datetime | None = None,
    ):
        self.resource = resource
        self.account = account
        self.time = time or datetime.now()


class ResourceUnavailable(AvillaEvent, Generic[R]):
    resource: R

    @property
    def ctx(self):
        return self.resource.to_selector().set_referent(self.resource)

    @property
    def mainline(self):
        return self.resource.mainline

    def __init__(
        self,
        resource: R,
        account: Selector,
        time: datetime | None = None,
    ):
        self.resource = resource
        self.account = account
        self.time = time or datetime.now()
