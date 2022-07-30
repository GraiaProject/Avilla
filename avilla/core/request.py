from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.platform import Land

if TYPE_CHECKING:
    from avilla.core.account import AbstractAccount
    from avilla.core.utilles.selector import Selector


@dataclass
class Request:
    id: str
    land: Land
    mainline: Selector
    sender: Selector
    account: AbstractAccount
    time: datetime

    request_type: str | None = None
    operator: Selector | None = None
    response: str | None = None

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
            request_id = f"{self.request_type}:{request_id}"
        return self.mainline.copy().request(request_id)
