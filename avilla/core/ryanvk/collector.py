from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, NoReturn as Never, cast

from typing_extensions import Unpack

from avilla.core.ryanvk.capability import CoreCapability


from .common.collect import BaseCollector
from .context import processing_protocol

if TYPE_CHECKING:
    from ..selector import Selector
    from ..account import AbstractAccount
    from ..context import Context
    from ..metadata import Metadata, MetadataRoute
    from ..protocol import BaseProtocol
    from ..selector import FollowsPredicater
    from .fn import PullFn


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TAccount = TypeVar("TAccount", bound="AbstractAccount")

TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")
TAccount1 = TypeVar("TAccount1", bound="AbstractAccount")


class AvillaPerformTemplate:
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
        self.artifacts["lookup"] = {}

    @property
    def _(self):
        class perform_template(AvillaPerformTemplate, self._base_ring3()):
            __native__ = True

        return perform_template


M = TypeVar("M", bound="Metadata")


class ProtocolCollector(Generic[TProtocol, TAccount], Collector):
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

        return perform_template[TProtocol, TAccount]

    def __post_collect__(self, cls: type[AvillaPerformTemplate]):
        super().__post_collect__(cls)
        if self.post_applying:
            if (protocol := processing_protocol.get(None)) is None:
                raise RuntimeError("expected processing protocol")
            protocol.isolate.apply(cls)

    def pull(
        self, target: str, route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M], **patterns: FollowsPredicater
    ):
        return self.entity(cast('PullFn[M]', CoreCapability.pull), (target, patterns), route)
