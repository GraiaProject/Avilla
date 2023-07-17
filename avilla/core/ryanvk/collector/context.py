from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from avilla.core.ryanvk._runtime import processing_isolate, processing_protocol
from avilla.core.ryanvk.collector.base import Access, BaseCollector, PerformTemplate

if TYPE_CHECKING:
    from avilla.core.account import BaseAccount
    from avilla.core.context import Context
    from avilla.core.metadata import Metadata
    from avilla.core.protocol import BaseProtocol


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TAccount = TypeVar("TAccount", bound="BaseAccount")

TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")
TAccount1 = TypeVar("TAccount1", bound="BaseAccount")

T = TypeVar("T")
T1 = TypeVar("T1")
M = TypeVar("M", bound="Metadata")


class ContextBasedPerformTemplate(PerformTemplate):
    __collector__: ClassVar[ContextCollector]

    context: Access[Context] = Access()

    @property
    def protocol(self):
        return self.context.protocol

    @property
    def account(self):
        return self.context.account


class ContextCollector(BaseCollector, Generic[TProtocol, TAccount]):
    post_applying: bool = False

    def __init__(self):
        super().__init__()

    @property
    def _(self):
        upper = super().get_collect_template()

        class LocalPerformTemplate(
            Generic[TProtocol1, TAccount1],
            ContextBasedPerformTemplate,
            upper,
        ):
            __native__ = True

            protocol: TProtocol1
            account: TAccount1

        return LocalPerformTemplate[TProtocol, TAccount]

    def __post_collect__(self, cls: type[ContextBasedPerformTemplate]):
        super().__post_collect__(cls)
        if self.post_applying:
            if (protocol := processing_protocol.get(None)) is None:
                if (isolate := processing_isolate.get(None)) is not None:
                    isolate.apply(cls)
                return

            protocol.isolate.apply(cls)
