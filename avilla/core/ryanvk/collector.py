from typing import TYPE_CHECKING, Generic, TypeVar

from avilla.core.utilles import classproperty
from .common.collect import BaseCollector


if TYPE_CHECKING:
    from avilla.core.protocol import BaseProtocol
    from avilla.core.account import AbstractAccount
    from avilla.core.context import Context


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TAccount = TypeVar("TAccount", bound="AbstractAccount")

TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")
TAccount1 = TypeVar("TAccount1", bound="AbstractAccount")


"""
artifacts! {
    .land {
        _ => {...}
        "qq"(override = true) => {...}

        .group {
            _ => {...}
            "..."(,,,) => {...}
        }
    }

    # and other that could be "chainmap-overrided", hybrid structure;
}
"""


class Collector(BaseCollector):
    def __init__(self):
        super().__init__()


    @classproperty
    @classmethod
    def protocol(cls):
        return ProtocolCollector


collect = Collector


class ProtocolCollector(Generic[TProtocol, TAccount], BaseCollector):
    @property
    def _(self):
        class perform_template(self._base_ring3(), Generic[TProtocol1, TAccount1]):
            __native__ = True

            context: Context
            protocol: TProtocol1
            account: TAccount1

            def __init__(self, context: Context):
                self.context = context
                self.protocol = context.protocol  # type: ignore
                self.account = context.account  # type: ignore

        return perform_template[TProtocol, TAccount]
