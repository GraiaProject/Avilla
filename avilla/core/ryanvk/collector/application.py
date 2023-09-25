from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from graia.ryanvk import Access, BasePerform

from .base import AvillaBaseCollector

if TYPE_CHECKING:
    from avilla.core.application import Avilla


T = TypeVar("T")
T1 = TypeVar("T1")


class ApplicationBasedPerformTemplate(BasePerform, native=True):
    __collector__: ClassVar[ApplicationCollector]

    avilla: Access[Avilla] = Access()


class ApplicationCollector(AvillaBaseCollector):
    post_applying: bool = False

    def __init__(self):
        super().__init__()

    @property
    def _(self):
        upper = super()._

        class LocalPerformTemplate(
            ApplicationBasedPerformTemplate,
            upper,
            native=True,
        ):
            ...

        return LocalPerformTemplate
