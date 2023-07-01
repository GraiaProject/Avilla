from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, cast

from typing_extensions import Unpack

from avilla.core.ryanvk.capability import CoreCapability

from .._runtime import processing_isolate, processing_protocol
from ..common.collect import BaseCollector
from ..descriptor.fetch import Fetch

if TYPE_CHECKING:
    from ...account import BaseAccount
    from ...context import Context
    from ...metadata import Metadata, MetadataRoute
    from ...protocol import BaseProtocol
    from ...selector import FollowsPredicater
    from ..descriptor.pull import PullFn


TProtocol = TypeVar("TProtocol", bound="BaseProtocol")
TAccount = TypeVar("TAccount", bound="BaseAccount")

TProtocol1 = TypeVar("TProtocol1", bound="BaseProtocol")
TAccount1 = TypeVar("TAccount1", bound="BaseAccount")

T = TypeVar("T")
T1 = TypeVar("T1")
M = TypeVar("M", bound="Metadata")


class ContextBasedPerformTemplate:
    __collector__: ClassVar[ContextCollector]

    context: Context
    protocol: BaseProtocol
    account: BaseAccount

    def __init__(self, context: Context):
        self.context = context
        self.protocol = context.protocol
        self.account = context.account


class ContextCollector(BaseCollector, Generic[TProtocol, TAccount]):
    post_applying: bool = False

    def __init__(self):
        super().__init__()
        self.artifacts["current_collection"] = {}

    def pull(
        self, target: str, route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M], **patterns: FollowsPredicater
    ):
        return self.entity(cast("PullFn[M]", CoreCapability.pull), (target, patterns), route)

    def fetch(self, resource_type: type[T]):  # type: ignore[reportInvalidTypeVarUse]
        return self.entity(Fetch, resource_type)

    @property
    def _(self):
        upper = super()._base_ring3()

        class perform_template(
            Generic[TProtocol1, TAccount1],
            ContextBasedPerformTemplate,
            upper,
        ):
            __native__ = True

            context: Context
            protocol: TProtocol1
            account: TAccount1

        return perform_template[TProtocol, TAccount]

    def __post_collect__(self, cls: type[ContextBasedPerformTemplate]):
        super().__post_collect__(cls)
        if self.post_applying:
            if (isolate := processing_isolate.get(None)) is not None:
                isolate.apply(cls)
            if (protocol := processing_protocol.get(None)) is None:
                raise RuntimeError("expected processing protocol")
            protocol.isolate.apply(cls)