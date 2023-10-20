from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from avilla.core.ryanvk.collector.base import AvillaBaseCollector
from graia.ryanvk import Access, BasePerform
from satori.account import Account

if TYPE_CHECKING:
    from avilla.satori.protocol import SatoriProtocol


T = TypeVar("T")
T1 = TypeVar("T1")


class ConnectionBasedPerformTemplate(BasePerform, native=True):
    __collector__: ClassVar[ConnectionCollector]

    protocol: Access[SatoriProtocol] = Access()
    connection: Access[Account] = Access()


class ConnectionCollector(AvillaBaseCollector):
    post_applying: bool = False

    @property
    def _(self):
        upper = super()._

        class PerformTemplate(
            ConnectionBasedPerformTemplate,
            upper,
            native=True,
        ):
            ...

        return PerformTemplate
