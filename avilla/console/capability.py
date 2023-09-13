from __future__ import annotations

from typing import Any, NoReturn, TypeVar

from nonechat.message import Element as ConsoleElement

from graia.amnesia.message import Element as GraiaElement
from graia.ryanvk import Capability, Fn, TypeOverload

CE = TypeVar("CE", bound=ConsoleElement)
GE = TypeVar("GE", bound=GraiaElement)

GE_T = TypeVar("GE_T", bound=NoReturn, contravariant=True)


class ConsoleCapability(Capability):
    @Fn.complex({TypeOverload(): ['event']})
    async def event_callback(self, event: Any) -> Any:
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def deserialize_element(self, element: Any) -> GraiaElement:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ["element"]})
    async def serialize_element(self, element: Any) -> ConsoleElement:  # type: ignore
        ...
