from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from avilla.core.ryanvk.collector.base import AvillaBaseCollector
from graia.ryanvk import Access, BasePerform

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount
    from avilla.telegram.bot.bot import TelegramBot

T = TypeVar("T")
T1 = TypeVar("T1")


class ExtBotBasedPerformTemplate(BasePerform, native=True):
    __collector__: ClassVar[InstanceCollector]

    instance: Access[TelegramBot] = Access()
    account: Access[TelegramAccount] = Access()


class InstanceCollector(AvillaBaseCollector):
    post_applying: bool = False

    @property
    def _(self):
        upper = super()._

        class PerformTemplate(
            ExtBotBasedPerformTemplate,
            upper,
            native=True,
        ):
            ...

        return PerformTemplate
