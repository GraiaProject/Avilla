from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from avilla.core.ryanvk.collector.base import AvillaBaseCollector, BasePerform
from graia.ryanvk import Access

if TYPE_CHECKING:
    from avilla.qqguild.tencent.connection.ws_client import QQGuildWsClientNetworking
    from avilla.qqguild.tencent.protocol import QQGuildProtocol


T = TypeVar("T")
T1 = TypeVar("T1")


class ConnectionBasedPerformTemplate(BasePerform, native=True):
    __collector__: ClassVar[ConnectionCollector]

    protocol: Access[QQGuildProtocol] = Access()
    connection: Access[QQGuildWsClientNetworking] = Access()


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
