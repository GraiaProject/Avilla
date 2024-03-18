from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar, overload

from flywheel.fn.base import Fn
from flywheel.fn.compose import FnCompose, OverloadRecorder
from flywheel.fn.record import FnRecord
from flywheel.overloads import SimpleOverload, TypeOverload
from typing_extensions import Unpack

from avilla.core.metadata import Metadata, MetadataRoute
from avilla.core.resource import Resource, T
from avilla.core.ryanvk.overloads import TargetOverload

if TYPE_CHECKING:
    from avilla.core.context import Context
    from avilla.core.selector import Selector


M = TypeVar("M", bound=Metadata)
MR = TypeVar("MR", bound=Metadata, covariant=True)
R = TypeVar("R", covariant=True)
Res = TypeVar("Res", bound=Resource, contravariant=True)
Res1 = TypeVar("Res1", bound=Resource, covariant=True)


class CoreCapability:
    # query = QuerySchema()

    target = TargetOverload("target")

    @Fn.declare
    class get_context(FnCompose):
        via = TargetOverload("via")
        novia = SimpleOverload("novia")

        def call(self, record: FnRecord, target: Selector, *, via: Selector | None = None) -> Context:
            entities = self.load(
                CoreCapability.target.dig(record, target),
                self.novia.dig(record, via) if via is None else self.via.dig(record, via),
            )

            if via is None:
                return entities.first(target=target)  # type: ignore

            return entities.first(target=target, via=via)

        class shapecall_novia(Protocol):
            def __call__(self, target: Selector) -> Context: ...

        class shapecall_via(Protocol):
            def __call__(self, target: Selector, via: Selector) -> Context: ...

        @overload
        def collect(self, recorder: OverloadRecorder[shapecall_via], target: str, via: str) -> None: ...

        @overload
        def collect(self, recorder: OverloadRecorder[shapecall_novia], target: str, via: None = None) -> None: ...

        def collect(self, recorder: OverloadRecorder, target: str, via: str | None = None):
            # TODO: 能否使用 predicator?

            recorder.use(CoreCapability.target, (target, {}))
            if via is None:
                recorder.use(self.novia, None)
            else:
                recorder.use(self.via, (via, {}))

    @Fn.declare
    class pull(FnCompose):
        route: SimpleOverload

        async def call(
            self, record: FnRecord, target: Selector, route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M]
        ) -> M:
            entities = self.load(CoreCapability.target.dig(record, target), self.route.dig(record, route))
            return await entities.first(target=target)

        class shapecall(Protocol[MR]):
            async def __call__(self, target: Selector) -> MR: ...

        def collect(
            self,
            recorder: OverloadRecorder[shapecall[M]],
            target: str,
            route: type[M] | MetadataRoute[Unpack[tuple[Any, ...]], M],
        ):
            recorder.use(CoreCapability.target, (target, {}))
            recorder.use(self.route, route)

    @Fn.declare
    class fetch(FnCompose):
        resource = TypeOverload("resource")

        async def call(self, record: FnRecord, resource: Resource[T]) -> T:
            entities = self.load(self.resource.dig(record, resource))
            return await entities.first(resource)

        class shapecall(Protocol[Res, Res1]):
            async def __call__(self: CoreCapability.fetch.shapecall[Res, Resource[T]], resource: Res) -> T: ...

        def collect(self, recorder: OverloadRecorder[shapecall[Res, Res]], resource: type[Res]):
            recorder.use(self.resource, resource)

    @Fn.declare
    class channel(FnCompose):
        def call(self, record: FnRecord, target: Selector) -> str:
            entities = self.load(CoreCapability.target.dig(record, target))
            return entities.first(target=target)

        class shapecall(Protocol):
            def __call__(self, target: Selector) -> str: ...

        def collect(self, recorder: OverloadRecorder[shapecall], target: str):
            recorder.use(CoreCapability.target, (target, {}))

    @Fn.declare
    class guild(FnCompose):
        def call(self, record: FnRecord, target: Selector) -> str:
            entities = self.load(CoreCapability.target.dig(record, target))
            return entities.first(target=target)

        class shapecall(Protocol):
            def __call__(self, target: Selector) -> str: ...

        def collect(self, recorder: OverloadRecorder[shapecall], target: str):
            recorder.use(CoreCapability.target, (target, {}))

    @Fn.declare
    class user(FnCompose):
        def call(self, record: FnRecord, target: Selector) -> str:
            entities = self.load(CoreCapability.target.dig(record, target))
            return entities.first(target=target)

        class shapecall(Protocol):
            def __call__(self, target: Selector) -> str: ...

        def collect(self, recorder: OverloadRecorder[shapecall], target: str):
            recorder.use(CoreCapability.target, (target, {}))

    # TODO: query
