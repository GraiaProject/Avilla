from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from graia.ryanvk import Access, BasePerform

from .base import AvillaBaseCollector

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


class ContextBasedPerformTemplate(BasePerform, native=True):
    __collector__: ClassVar[ContextCollector]

    context: Access[Context] = Access()

    @property
    def protocol(self):
        return self.context.protocol

    @property
    def account(self):
        return self.context.account


class ContextCollector(AvillaBaseCollector, Generic[TProtocol, TAccount]):
    post_applying: bool = False

    def __init__(self):
        super().__init__()

    @property
    def _(self):
        upper = super()._

        class LocalPerformTemplate(
            Generic[TProtocol1, TAccount1],
            ContextBasedPerformTemplate,
            upper,
            native=True,
        ):
            protocol: TProtocol1
            account: TAccount1

        return LocalPerformTemplate[TProtocol, TAccount]
