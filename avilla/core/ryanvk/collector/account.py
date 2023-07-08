from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from .._runtime import processing_isolate, processing_protocol
from .base import BaseCollector

if TYPE_CHECKING:
    from ...account import BaseAccount
    from ...protocol import BaseProtocol


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TAccount = TypeVar("TAccount", bound="BaseAccount")

TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")
TAccount1 = TypeVar("TAccount1", bound="BaseAccount")

T = TypeVar("T")
T1 = TypeVar("T1")


class AccountBasedPerformTemplate:
    __collector__: ClassVar[AccountCollector]

    protocol: BaseProtocol
    account: BaseAccount


class AccountCollector(BaseCollector, Generic[TProtocol, TAccount]):
    post_applying: bool = False

    def __init__(self):
        super().__init__()
        self.artifacts["current_collection"] = {}

    @property
    def _(self):
        upper = super().get_collect_template()

        class PerformTemplate(
            Generic[TProtocol1, TAccount1],
            AccountBasedPerformTemplate,
            upper,
        ):
            __native__ = True

            protocol: TProtocol1
            account: TAccount1

            def __init__(self, protocol: TProtocol1, account: TAccount1):
                self.protocol = protocol
                self.account = account

        assert issubclass(PerformTemplate, AccountBasedPerformTemplate)
        return PerformTemplate[TProtocol, TAccount]

    def __post_collect__(self, cls: type[AccountBasedPerformTemplate]):
        super().__post_collect__(cls)
        if self.post_applying:
            if (isolate := processing_isolate.get(None)) is not None:
                isolate.apply(cls)
            if (protocol := processing_protocol.get(None)) is None:
                raise RuntimeError("expected processing protocol")
            protocol.isolate.apply(cls)
