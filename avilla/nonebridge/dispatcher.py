from __future__ import annotations

from asyncio import Queue
from typing import Generic, TypeVar

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import (
    DispatcherInterface as DispatcherInterface,
)

T = TypeVar("T", bound=Dispatchable)


class AllEventQueue(BaseDispatcher, Generic[T]):
    queue: Queue[T]

    def __init__(self, *, maxsize=20) -> None:
        self.queue = Queue(maxsize=maxsize)

    async def beforeExecution(self, interface: DispatcherInterface[T]):
        if interface.event.__dict__.get("$queued"):
            return

        interface.event.__dict__["$queued"] = True
        await self.queue.put(interface.event)

    async def catch(self, interface: DispatcherInterface):
        return
