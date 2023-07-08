from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from .._runtime import processing_application, processing_isolate
from .base import BaseCollector

if TYPE_CHECKING:
    from avilla.core.application import Avilla


T = TypeVar("T")
T1 = TypeVar("T1")


class ApplicationBasedPerformTemplate:
    __collector__: ClassVar[ApplicationCollector]

    avilla: Avilla


class ApplicationCollector(BaseCollector):
    post_applying: bool = False

    def __init__(self):
        super().__init__()
        self.artifacts["lookup"] = {}

    @property
    def _(self):
        upper = super().get_collect_template()

        class PerformTemplate(
            ApplicationBasedPerformTemplate,
            upper,
        ):
            __native__ = True

            def __init__(self, avilla: Avilla):
                self.avilla = avilla

        return PerformTemplate

    def __post_collect__(self, cls: type[ApplicationBasedPerformTemplate]):
        super().__post_collect__(cls)
        if self.post_applying:
            if (isolate := processing_isolate.get(None)) is not None:
                isolate.apply(cls)
            if (application := processing_application.get(None)) is not None:
                application.isolate.apply(cls)
