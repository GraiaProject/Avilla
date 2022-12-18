from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.abstract.event import AvillaEvent
from avilla.core.abstract.request import Request

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class RequestEvent(AvillaEvent):
    request: Request

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface[RequestEvent]):
            if interface.annotation is Request:
                return interface.event.request
            return await super().catch(interface)


class RequestReceived(RequestEvent):
    pass


class RequestAccepted(RequestEvent):
    pass


class RequestRejected(RequestEvent):
    pass


class RequestIgnored(RequestEvent):
    pass


class RequestCancelled(RequestEvent):
    pass
