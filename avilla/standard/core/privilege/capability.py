from __future__ import annotations

from typing import Protocol
from datetime import timedelta

from flywheel import Fn, FnCompose, FnRecord, OverloadRecorder
from avilla.core.ryanvk import TargetOverload
from avilla.core.selector import Selector


@Fn.declare
class upgrade_privilege(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector, dest: str | None = None) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target, dest)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, dest: str | None = None) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class downgrade_privilege(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector, dest: str | None = None) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target, dest)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, dest: str | None = None) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class mute_entity(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector, duration: timedelta) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target, duration)

    class shapecall(Protocol):
        async def __call__(self, target: Selector, duration: timedelta) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class unmute_entity(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class mute_all(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class unmute_all(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class ban_entity(FnCompose):
    target = TargetOverload("target")

    async def call(
        self, record: FnRecord, target: Selector, *, duration: timedelta | None = None, reason: str | None = None
    ) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target, duration, reason)

    class shapecall(Protocol):
        async def __call__(
            self, target: Selector, duration: timedelta | None = None, reason: str | None = None
        ) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))


@Fn.declare
class unban_entity(FnCompose):
    target = TargetOverload("target")

    async def call(self, record: FnRecord, target: Selector) -> None:
        entities = self.load(self.target.dig(record, target))

        return await entities.first(target)

    class shapecall(Protocol):
        async def __call__(self, target: Selector) -> None: ...

    def collect(self, recorder: OverloadRecorder[shapecall], target: str):
        recorder.use(self.target, (target, {}))
