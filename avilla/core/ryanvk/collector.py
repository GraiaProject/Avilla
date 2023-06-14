from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from .common.collect import BaseCollector
from .context import processing_protocol

if TYPE_CHECKING:
    from ..account import AbstractAccount
    from ..context import Context
    from ..protocol import BaseProtocol


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TAccount = TypeVar("TAccount", bound="AbstractAccount")

TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")
TAccount1 = TypeVar("TAccount1", bound="AbstractAccount")


class _AvillaPerformTemplate:
    __collector__: ClassVar[BaseCollector]

    context: Context
    protocol: BaseProtocol
    account: AbstractAccount

    def __init__(self, context: Context):
        self.context = context
        self.protocol = context.protocol
        self.account = context.account

class Collector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.artifacts['lookup'] = {}

    @property
    def _(self):
        class perform_template(_AvillaPerformTemplate, self._base_ring3()):
            __native__ = True

        return perform_template

class ProtocolCollector(Generic[TProtocol, TAccount], BaseCollector):
    post_applying: bool = False

    def __init__(self):
        super().__init__()

    @property
    def _(self):
        class perform_template(super()._, Generic[TProtocol1, TAccount1]):
            __native__ = True

            context: Context
            protocol: TProtocol1
            account: TAccount1

            def __init__(self, context: Context):
                self.context = context
                self.protocol = context.protocol  # type: ignore
                self.account = context.account  # type: ignore

        return perform_template[TProtocol, TAccount]

    def __post_collect__(self, cls: type[_AvillaPerformTemplate]):
        super().__post_collect__(cls)
        if self.post_applying:
            if (protocol := processing_protocol.get(None)) is None:
                raise RuntimeError("expected processing protocol")
            protocol.isolate.apply(cls)