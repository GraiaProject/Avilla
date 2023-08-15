from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from graia.ryanvk import Access, BasePerform

from .base import AvillaBaseCollector

if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")

T = TypeVar("T")
T1 = TypeVar("T1")


class ProtocolBasedPerformTemplate(BasePerform, native=True):
    __collector__: ClassVar[ProtocolCollector]

    protocol: Access[BaseProtocol] = Access()


class ProtocolCollector(AvillaBaseCollector, Generic[TProtocol]):
    post_applying: bool = False

    def __init__(self):
        super().__init__()

    @property
    def _(self):
        upper = super()._

        class LocalPerformTemplate(
            Generic[TProtocol1],
            ProtocolBasedPerformTemplate,
            upper,
            native=True,
        ):
            protocol: TProtocol1

        return LocalPerformTemplate[TProtocol]
