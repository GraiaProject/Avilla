from __future__ import annotations

from typing import Protocol

from flywheel import Fn, FnCompose, FnRecord, OverloadRecorder
from avilla.core.ryanvk import TargetOverload
from avilla.core.selector import Selector

@Fn.declare
class accept_request(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector):
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class reject_request(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector, reason: str | None = None, forever: bool = False):
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target, reason, forever)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, reason: str | None, forever: bool) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class cancel_request(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector):
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class ignore_request(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector):
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))
