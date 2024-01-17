from __future__ import annotations

from typing import ClassVar, Generic, TypeVar

from avilla.core.flywheel import BasePerform, InstanceOf, BaseCollector

from avilla.core.account import BaseAccount
from avilla.core.application import Avilla
from avilla.core.protocol import BaseProtocol
from avilla.core.context import Context


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TAccount = TypeVar("TAccount", bound="BaseAccount")

TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")
TAccount1 = TypeVar("TAccount1", bound="BaseAccount")

T = TypeVar("T")
T1 = TypeVar("T1")


class AccountBasedPerformTemplate(BasePerform, keep_native=True):
    __collector__: ClassVar[AccountCollector]

    protocol = InstanceOf(BaseProtocol)
    account = InstanceOf(BaseAccount)

    @property
    def avilla(self):
        return self.protocol.avilla

    @property
    def broadcast(self):
        return self.avilla.broadcast


class AccountCollector(BaseCollector, Generic[TProtocol, TAccount]):
    @property
    def _(self):
        upper = super()._

        class LocalPerformTemplate(
            Generic[TProtocol1, TAccount1],
            AccountBasedPerformTemplate,
            upper,
            keep_native=True,
        ):
            protocol: TProtocol1
            account: TAccount1

        return LocalPerformTemplate[TProtocol, TAccount]


class ApplicationBasedPerformTemplate(BasePerform, keep_native=True):
    __collector__: ClassVar[ApplicationCollector]

    avilla = InstanceOf(Avilla)


class ApplicationCollector(BaseCollector):
    @property
    def _(self):
        upper = super()._

        class LocalPerformTemplate(
            ApplicationBasedPerformTemplate,
            upper,
            keep_native=True,
        ):
            ...

        return LocalPerformTemplate

class ContextBasedPerformTemplate(BasePerform, keep_native=True):
    __collector__: ClassVar[ContextCollector]

    context = InstanceOf(Context)

    @property
    def protocol(self):
        return self.context.protocol

    @property
    def account(self):
        return self.context.account

    @property
    def avilla(self):
        return self.context.avilla


class ContextCollector(BaseCollector, Generic[TProtocol, TAccount]):
    @property
    def _(self):
        upper = super()._

        class LocalPerformTemplate(
            Generic[TProtocol1, TAccount1],
            ContextBasedPerformTemplate,
            upper,
            keep_native=True,
        ):
            protocol: TProtocol1
            account: TAccount1

        return LocalPerformTemplate[TProtocol, TAccount]



class ProtocolBasedPerformTemplate(BasePerform, keep_native=True):
    __collector__: ClassVar[ProtocolCollector]

    protocol = InstanceOf(BaseProtocol)


class ProtocolCollector(BaseCollector, Generic[TProtocol]):
    @property
    def _(self):
        upper = super()._

        class LocalPerformTemplate(
            Generic[TProtocol1],
            ProtocolBasedPerformTemplate,
            upper,
            keep_native=True,
        ):
            protocol: TProtocol1

        return LocalPerformTemplate[TProtocol]
