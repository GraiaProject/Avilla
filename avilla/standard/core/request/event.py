from __future__ import annotations

from dataclasses import dataclass

from avilla.core.event import AvillaEvent
from avilla.core.request import Request
from graia.broadcast.interfaces.dispatcher import DispatcherInterface


@dataclass
class RequestEvent(AvillaEvent):
    request: Request

    class Dispatcher(AvillaEvent.Dispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface[RequestEvent]):
            if interface.annotation is Request:
                return interface.event.request
            if interface.name == "sender":
                return interface.event.request.sender
            return await AvillaEvent.Dispatcher.catch(interface)


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
