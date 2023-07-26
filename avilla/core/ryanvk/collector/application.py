from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from avilla.core.ryanvk.collector.base import BaseCollector, PerformTemplate
from avilla.core.ryanvk.endpoint import Access

if TYPE_CHECKING:
    from avilla.core.application import Avilla


T = TypeVar("T")
T1 = TypeVar("T1")


class ApplicationBasedPerformTemplate(PerformTemplate, native=True):
    __collector__: ClassVar[ApplicationCollector]

    avilla: Access[Avilla] = Access()


class ApplicationCollector(BaseCollector):
    post_applying: bool = False

    def __init__(self):
        super().__init__()

    @property
    def _(self):
        upper = super().get_collect_template()

        class LocalPerformTemplate(
            ApplicationBasedPerformTemplate,
            upper,
            native=True,
        ):
            ...

        return LocalPerformTemplate
