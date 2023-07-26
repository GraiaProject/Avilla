from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from avilla.core.ryanvk.collector.base import BaseCollector, PerformTemplate
from avilla.core.ryanvk.endpoint import Access

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")

T = TypeVar("T")
T1 = TypeVar("T1")


class ProtocolBasedPerformTemplate(PerformTemplate, native=True):
    __collector__: ClassVar[ProtocolCollector]

    protocol: Access[BaseProtocol] = Access()


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
            native=True,
        ):
            protocol: TProtocol1

        return LocalPerformTemplate[TProtocol]
