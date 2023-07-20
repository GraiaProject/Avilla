from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

if TYPE_CHECKING:
    from avilla.core.application import Avilla


@dataclass
class AvillaLifecycleEvent(Dispatchable):
    """指示有关应用 (Avilla) 的事件."""

    avilla: Avilla

    class Dispatcher(BaseDispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[AvillaLifecycleEvent]):
            from avilla.core.application import Avilla

            if interface.annotation is Avilla:
                return interface.event.avilla


class ApplicationClosing(AvillaLifecycleEvent):
    """指示 Avilla 正在关闭."""


class ApplicationClosed(AvillaLifecycleEvent):
    """指示 Avilla 已经关闭."""


class ApplicationPreparing(AvillaLifecycleEvent):
    """指示 Avilla 正在准备."""


class ApplicationReady(AvillaLifecycleEvent):
    """指示 Avilla 已准备完毕."""
