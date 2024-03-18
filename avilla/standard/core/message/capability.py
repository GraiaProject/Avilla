from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

from graia.amnesia.message import MessageChain

from flywheel import Fn, FnCompose, FnRecord, OverloadRecorder
from avilla.core.ryanvk import TargetOverload
from avilla.core.selector import Selector
from avilla.core.builtins.capability import CoreCapability

if TYPE_CHECKING:
    from avilla.core.message import Message

# MessageFetch => rs.pull(Message, target=...)


@Fn.declare
class send_message(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector, message: MessageChain, *, reply: Selector | None = None):
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target, message, reply=reply)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, message: MessageChain, *, reply: Selector | None = None): ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class revoke_message(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector):
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector): ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class edit_message(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector, content: MessageChain):
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target, content)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, content: MessageChain): ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


async def pull_message(target: Selector) -> Message:
    return await CoreCapability.pull(target, Message)
