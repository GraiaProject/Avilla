from __future__ import annotations
from typing import Protocol

from flywheel import Fn, FnCompose, FnRecord, OverloadRecorder
from avilla.core.ryanvk import TargetOverload
from avilla.core.selector import Selector


@Fn.declare
class start_activity(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector):
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target=target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector): ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))
