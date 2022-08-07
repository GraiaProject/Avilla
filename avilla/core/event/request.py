from __future__ import annotations

from typing import TYPE_CHECKING

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.core.request import Request

from . import AvillaEvent

if TYPE_CHECKING:
    from datetime import datetime


class RequestEvent(AvillaEvent):
    request: Request

    @property
    def mainline(self):
        return self.request.mainline

    @property
    def ctx(self):
        return self.request.sender

    def __init__(
        self,
        request: Request,
        time: datetime | None = None,
    ):
        self.request = request
        super().__init__(request.account, time=time)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface[RequestEvent]):
            if interface.annotation is Request:
                return interface.event.request


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
