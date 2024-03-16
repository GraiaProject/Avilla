from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from avilla.standard.core.request.capability import RequestCapability

from ._runtime import cx_context
from .metadata import Metadata
from .platform import Land

if TYPE_CHECKING:
    from .account import BaseAccount
    from .selector import Selector


@dataclass
class Request(Metadata):
    id: str
    land: Land
    scene: Selector
    sender: Selector
    account: BaseAccount
    time: datetime

    request_type: str | None = None
    operator: Selector | None = None
    response: str | None = None

    message: str | None = None

    @property
    def solved(self) -> bool:
        return self.response is not None

    @property
    def pending(self) -> bool:
        return self.response is None

    @property
    def accepted(self) -> bool:
        return self.response == "accept"

    @property
    def rejected(self) -> bool:
        return self.response == "reject"

    @property
    def cannelled(self) -> bool:
        return self.response == "cancel"

    @property
    def ignored(self) -> bool:
        return self.response == "ignore"

    def to_selector(self) -> Selector:
        request_id = self.id
        if self.request_type is not None:
            request_id = f"{self.request_type}@{request_id}"
        return self.scene.request(request_id)

    async def accept(self):
        return await cx_context.get()[RequestCapability.accept](self.to_selector())

    async def reject(self, reason: str | None = None, forever: bool = False):
        return await cx_context.get()[RequestCapability.reject](self.to_selector(), reason, forever)

    async def cancel(self):
        return await cx_context.get()[RequestCapability.cancel](self.to_selector())

    async def ignore(self):
        return await cx_context.get()[RequestCapability.ignore](self.to_selector())
