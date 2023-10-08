from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING, Any, ClassVar

from .endpoint import Endpoint

if TYPE_CHECKING:
    from graia.ryanvk.staff import Staff

    from .collector import BaseCollector


class BasePerform:
    __collector__: ClassVar[BaseCollector]
    # spec said one perform declare / class only binds to one collector instance.
    # multi to single or reversed behavior or settings are both denied in spec,
    # and, be suggested, actually coding. 

    __static__: ClassVar[bool] = True
    # when a perform is static, its lifespan won't execute,
    # which means dynamic endpoint cannot be used in the perform.

    staff: Staff

    def __init__(self, staff: Staff) -> None:
        self.staff = staff

    def __post_init__(self):
        ...

    @classmethod
    def apply_to(cls, map: dict[Any, Any]):
        map.update(cls.__collector__.artifacts)

    @classmethod
    def endpoints(cls):
        return [(k, v) for k, v in cls.__dict__.items() if isinstance(v, Endpoint)]

    @asynccontextmanager
    async def lifespan(self):
        async with AsyncExitStack() as stack:
            for _, v in self.endpoints():
                await stack.enter_async_context(v.lifespan(self))
            yield self

    @classmethod
    def __post_collected__(cls, collect: BaseCollector):
        ...

    def __init_subclass__(cls, *, native: bool = False, static: bool = True) -> None:
        if native:
            return

        collector = cls.__collector__
        cls.__static__ = static

        for i in collector.collected_callbacks:
            i(cls)

        cls.__post_collected__(collector)
