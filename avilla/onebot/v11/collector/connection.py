from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from avilla.core.ryanvk._runtime import processing_isolate, processing_protocol
from avilla.core.ryanvk.collector.base import BaseCollector

if TYPE_CHECKING:
    from ..protocol import OneBot11Protocol
    from ..net.ws_client import OneBot11WsClientNetworking


T = TypeVar("T")
T1 = TypeVar("T1")


class ConnectionBasedPerformTemplate:
    __collector__: ClassVar[ConnectionCollector]

    protocol: OneBot11Protocol
    connection: OneBot11WsClientNetworking  # TODO: Network overload

    def __init__(self, protocol: OneBot11Protocol, connection: OneBot11WsClientNetworking):
        self.protocol = protocol
        self.connection = connection


class ConnectionCollector(BaseCollector):
    post_applying: bool = False

    def __init__(self):
        super().__init__()
        self.artifacts["current_collection"] = {}

    @property
    def _(self):
        upper = super().get_collect_template()

        class PerformTemplate(
            ConnectionBasedPerformTemplate,
            upper,
        ):
            __native__ = True

        return PerformTemplate

    def __post_collect__(self, cls: type[ConnectionBasedPerformTemplate]):
        super().__post_collect__(cls)
        if self.post_applying:
            if (isolate := processing_isolate.get(None)) is not None:
                isolate.apply(cls)
            if (protocol := processing_protocol.get(None)) is None:
                raise RuntimeError("expected processing protocol")
            protocol.isolate.apply(cls)
