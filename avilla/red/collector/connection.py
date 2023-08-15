from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from avilla.core.ryanvk.collector.base import AvillaBaseCollector, BasePerform
from graia.ryanvk import Access

if TYPE_CHECKING:
    from avilla.red.net.ws_client import RedWsClientNetworking
    from avilla.red.protocol import RedProtocol


T = TypeVar("T")
T1 = TypeVar("T1")


class ConnectionBasedPerformTemplate(BasePerform, native=True):
    __collector__: ClassVar[ConnectionCollector]

    protocol: Access[RedProtocol] = Access()
    connection: Access[RedWsClientNetworking] = Access()


class ConnectionCollector(AvillaBaseCollector):
    post_applying: bool = False

    @property
    def _(self):
        upper = super()._

        class PerformTemplate(
            ConnectionBasedPerformTemplate,
            upper,
        ):
            __native__ = True

        return PerformTemplate
