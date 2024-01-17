from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, ClassVar

from .collector import BaseCollector
from .perform import BasePerform

if TYPE_CHECKING:
    from .fn import Fn
    from .fn.base import FnComposeCallReturnType, FnMethodComposeCls, collectShape
    from .typing import P, R, inTC


class CapabilityPerform(BasePerform, keep_native=True):
    __collector__: ClassVar[CapabilityCollector]

    __allow_incomplete__: ClassVar[bool] = False

    def __init_subclass__(cls, *, keep_native: bool = False, allow_incomplete: bool = False) -> None:
        cls.__allow_incomplete__ = allow_incomplete

        return super().__init_subclass__(keep_native=keep_native)


class CapabilityCollector(BaseCollector):
    definations: list[Fn]

    def __init__(self, artifacts: dict[Any, Any] | None = None) -> None:
        super().__init__(artifacts)

        self.definations = []

    @property
    def _(self):
        class LocalPerformTemplate(CapabilityPerform, keep_native=True):
            __collector__ = self

        return LocalPerformTemplate

    def compose(self, *, weird: bool = False):
        def wrapper(
            compose_cls: type[FnMethodComposeCls[collectShape, Callable[P, FnComposeCallReturnType[R]]]]
        ) -> Fn[collectShape, Callable[P, R]]:
            f = Fn.compose(compose_cls)
            if not weird:
                self.definations.append(f)
            return f

        return wrapper

    def symmetric(self, *, weird: bool = False):
        def wrapper(entity: inTC) -> Fn[Callable[[inTC], Any], inTC]:
            f = Fn.symmetric(entity)
            if not weird:
                self.definations.append(f)
            return f

        return wrapper


def capability():
    return CapabilityCollector()
