from __future__ import annotations

from typing import Protocol

from flywheel import Fn, FnCompose, FnRecord, OverloadRecorder
from avilla.core.ryanvk import TargetOverload
from avilla.core.selector import Selector

#    # @Fn.with_overload({
#    #    TargetOverload(): ['target']
#    # })
#    # async def request_join(self, solver: Isolate) -> None:
#    #     ...
#
#    # TODO: invite someone to join the scene
#
#
# class RequestJoinCapability(Capability):
#    @Fn
#    async def on_question(self, target: Selector, question_id: str, question: str, optional: bool) -> str | None:
#        ...
#
#    @Fn
#    async def on_reason(self, target: Selector) -> str | None:
#        ...
#
#    @Fn
#    async def on_term(self, term: tuple[Literal["string", "url"] | str, str]) -> bool:
#        ...
#
#


@Fn.declare
class leave_scene(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class disband_scene(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class remove_member(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector, reason: str | None = None) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target, reason)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, reason: str | None) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class terminate_relationship(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))
