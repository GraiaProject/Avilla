from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING, Any, ClassVar

from .endpoint import Endpoint

if TYPE_CHECKING:
    from graia.ryanvk.staff import Staff

    from .collector import BaseCollector


class BasePerform:
    __collector__: ClassVar[BaseCollector]

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

    def __init_subclass__(cls, *, native: bool = False) -> None:
        if native:
            return

        collector = cls.__collector__

        for i in collector.collected_callbacks:
            i(cls)

        cls.__post_collected__(collector)
