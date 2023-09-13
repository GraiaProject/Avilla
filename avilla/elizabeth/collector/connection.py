from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from avilla.core.ryanvk.collector.base import AvillaBaseCollector
from graia.ryanvk import Access, BasePerform

if TYPE_CHECKING:
    from avilla.elizabeth.connection.ws_client import ElizabethWsClientNetworking
    from avilla.elizabeth.protocol import ElizabethProtocol


T = TypeVar("T")
T1 = TypeVar("T1")


class ConnectionBasedPerformTemplate(BasePerform, native=True):
    __collector__: ClassVar[ConnectionCollector]

    protocol: Access[ElizabethProtocol] = Access()
    connection: Access[ElizabethWsClientNetworking] = Access()


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
