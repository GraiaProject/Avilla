from __future__ import annotations

from typing import TYPE_CHECKING

from graia.ryanvk import Access, BasePerform

if TYPE_CHECKING:
    from ..service import NoneBridgeService  # noqa


class ServiceAccess(Access["NoneBridgeService"]):
    name = "nonebridge.service"

    def __set_name__(self, owner: type, name: str):
        return


class NoneBridgePerform(BasePerform, native=True):
    service = ServiceAccess()
