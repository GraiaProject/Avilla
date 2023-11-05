from __future__ import annotations

import io
import os

from avilla.core.ryanvk import Capability, Fn, TargetOverload
from avilla.core.selector import Selector
from avilla.standard.telegram.poll.metadata import PollType


class PollPublish(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def publish(
        self,
        target: Selector,
        question: str,
        options: list[str],
        type: PollType = PollType.REGULAR,
        *,
        is_anonymous: bool = False,
        allow_multiple_answers: bool = False,
        correct_option_id: int | None = None,
        explanation: str | None = None,
        explanation_parse_mode: str | None = None,
        open_period: int | None = None,
        close_date: int | None = None,
    ) -> Selector:
        """发布群公告

        target 是公告发布到的群
        """
        ...


class PollStop(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def delete(self, target: Selector) -> None:
        """删除群公告

        target 是群公告的 id
        """
        ...
