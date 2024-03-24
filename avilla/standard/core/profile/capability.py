from __future__ import annotations
from typing import Protocol
from avilla.core.metadata import Route
from avilla.core.resource import Resource
from flywheel import Fn, FnCompose, FnRecord, OverloadRecorder, SimpleOverload
from avilla.core.ryanvk import TargetOverload
from avilla.core.selector import Selector


@Fn.declare
class set_summary_name(FnCompose):
    target = TargetOverload("target")
    route = SimpleOverload("route")

    async def call(self, record: FnRecord, target: Selector, route: Route, name: str) -> None:
        entities = self.load(self.target.dig(record, target), self.route.dig(record, route))
        await entities.first(target, name)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, name: str) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str, route: Route):
        recorder.use(self.target, (target, {}))
        recorder.use(self.route, (route, {}))


@Fn.declare
class unset_summary_name(FnCompose):
    target = TargetOverload("target")
    route = SimpleOverload("route")

    async def call(self, record: FnRecord, target: Selector, route: Route) -> None:
        entities = self.load(self.target.dig(record, target), self.route.dig(record, route))
        await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str, route: Route):
        recorder.use(self.target, (target, {}))
        recorder.use(self.route, (route, {}))


@Fn.declare
class set_summary_description(FnCompose):
    target = TargetOverload("target")
    route = SimpleOverload("route")

    async def call(self, record: FnRecord, target: Selector, route: Route, description: str) -> None:
        entities = self.load(self.target.dig(record, target), self.route.dig(record, route))
        await entities.first(target, description)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, description: str) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str, route: Route):
        recorder.use(self.target, (target, {}))
        recorder.use(self.route, (route, {}))


@Fn.declare
class unset_summary_description(FnCompose):
    target = TargetOverload("target")
    route = SimpleOverload("route")

    async def call(self, record: FnRecord, target: Selector, route: Route) -> None:
        entities = self.load(self.target.dig(record, target), self.route.dig(record, route))
        await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str, route: Route):
        recorder.use(self.target, (target, {}))
        recorder.use(self.route, (route, {}))


@Fn.declare
class set_nickname(FnCompose):
    target = TargetOverload("target")
    route = SimpleOverload("route")

    async def call(self, record: FnRecord, target: Selector, route: Route, nickname: str) -> None:
        entities = self.load(self.target.dig(record, target), self.route.dig(record, route))
        await entities.first(target, nickname)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, nickname: str) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str, route: Route):
        recorder.use(self.target, (target, {}))
        recorder.use(self.route, (route, {}))


@Fn.declare
class unset_nickname(FnCompose):
    target = TargetOverload("target")
    route = SimpleOverload("route")

    async def call(self, record: FnRecord, target: Selector, route: Route) -> None:
        entities = self.load(self.target.dig(record, target), self.route.dig(record, route))
        await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str, route: Route):
        recorder.use(self.target, (target, {}))
        recorder.use(self.route, (route, {}))


@Fn.declare
class set_badge(FnCompose):
    target = TargetOverload("target")
    route = SimpleOverload("route")

    async def call(self, record: FnRecord, target: Selector, route: Route, badge: str) -> None:
        entities = self.load(self.target.dig(record, target), self.route.dig(record, route))
        await entities.first(target, badge)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, badge: str) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str, route: Route):
        recorder.use(self.target, (target, {}))
        recorder.use(self.route, (route, {}))


@Fn.declare
class unset_badge(FnCompose):
    target = TargetOverload("target")
    route = SimpleOverload("route")

    async def call(self, record: FnRecord, target: Selector, route: Route) -> None:
        entities = self.load(self.target.dig(record, target), self.route.dig(record, route))
        await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str, route: Route):
        recorder.use(self.target, (target, {}))
        recorder.use(self.route, (route, {}))


@Fn.declare
class get_avatar(FnCompose):
    target = TargetOverload("target")

    def call(self, record: FnRecord, target: Selector) -> Resource[bytes]:
        entities = self.load(self.target.dig(record, target))
        return entities.first(target)

    class shapecall(Protocol):
        def __call__(self, target: Selector) -> Resource[bytes]: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))
