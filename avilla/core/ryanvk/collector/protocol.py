from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from .._runtime import processing_isolate, processing_protocol
from .base import BaseCollector, ComponentEntrypoint, PerformTemplate

if TYPE_CHECKING:
    from ...protocol import BaseProtocol


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")

T = TypeVar("T")
T1 = TypeVar("T1")


class ProtocolBasedPerformTemplate(PerformTemplate):
    __collector__: ClassVar[ProtocolCollector]

    protocol: ComponentEntrypoint[BaseProtocol] = ComponentEntrypoint()


class ProtocolCollector(BaseCollector, Generic[TProtocol]):
    post_applying: bool = False

    def __init__(self):
        super().__init__()

    @property
    def _(self):
        upper = super().get_collect_template()

        class LocalPerformTemplate(
            Generic[TProtocol1],
            ProtocolBasedPerformTemplate,
            upper,
        ):
            __native__ = True

            protocol: TProtocol1

        return LocalPerformTemplate[TProtocol]

    def __post_collect__(self, cls: type[ProtocolBasedPerformTemplate]):
        super().__post_collect__(cls)
        if self.post_applying:
            if (protocol := processing_protocol.get(None)) is None:
                if (isolate := processing_isolate.get(None)) is not None:
                    isolate.apply(cls)
                return
            
            protocol.isolate.apply(cls)
            
