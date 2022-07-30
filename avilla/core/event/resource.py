from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Generic, TypeVar

from avilla.core.event import AvillaEvent
from avilla.core.resource import Resource

if TYPE_CHECKING:
    from avilla.core.account import AbstractAccount

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
        account: AbstractAccount,
        time: datetime | None = None,
    ):
        self.resource = resource
        super().__init__(account, time=time)


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
        account: AbstractAccount,
        time: datetime | None = None,
    ):
        self.resource = resource
        super().__init__(account, time=time)
