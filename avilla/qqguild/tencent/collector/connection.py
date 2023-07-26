from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from avilla.core.ryanvk.collector.base import BaseCollector, PerformTemplate
from avilla.core.ryanvk.endpoint import Access

if TYPE_CHECKING:
    from avilla.qqguild.tencent.connection.ws_client import QQGuildWsClientNetworking
    from avilla.qqguild.tencent.protocol import QQGuildProtocol


T = TypeVar("T")
T1 = TypeVar("T1")


class ConnectionBasedPerformTemplate(PerformTemplate, native=True):
    __collector__: ClassVar[ConnectionCollector]

    protocol: Access[QQGuildProtocol] = Access()
    connection: Access[QQGuildWsClientNetworking] = Access()


class ConnectionCollector(BaseCollector):
    post_applying: bool = False

    @property
    def _(self):
        upper = super().get_collect_template()

        class PerformTemplate(
            ConnectionBasedPerformTemplate,
            upper,
            native=True,
        ):
            ...

        return PerformTemplate
