from __future__ import annotations

from avilla.core.ryanvk import Capability, Fn, TargetOverload
from avilla.core.selector import Selector
from avilla.standard.telegram.poll.metadata import PollKind


class PollPublish(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def publish(
        self,
        target: Selector,
        question: str,
        options: list[str],
        kind: PollKind = PollKind.REGULAR,
        *,
        is_anonymous: bool = False,
        allow_multiple_answers: bool = False,
        correct_option_id: int | None = None,
        explanation: str | None = None,
        explanation_parse_mode: str | None = None,
        open_period: int | None = None,
        close_date: int | None = None,
    ) -> Selector:
        ...


class PollStop(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def stop(self, target: Selector) -> None:
        ...
