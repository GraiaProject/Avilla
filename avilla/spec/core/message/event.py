from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.amnesia.message import __message_chain_class__

from avilla.core.event import AvillaEvent

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface

    from avilla.core.message import Message
    from avilla.core.selector import Selector


@dataclass
class MessageReceived(AvillaEvent):
    message: Message

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[MessageReceived]):
            if interface.annotation is interface.event.message.__class__:
                return interface.event.message
            elif interface.annotation is __message_chain_class__:
                return interface.event.message.content
            return await super().catch(interface)


@dataclass
class MessageEdited(AvillaEvent):
    message: Message
    operator: Selector
    past: __message_chain_class__
    current: __message_chain_class__

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[MessageEdited]):
            if interface.annotation is Message:
                return interface.event.message
            elif interface.annotation is __message_chain_class__:
                return interface.event.current
            return await super().catch(interface)


@dataclass
class MessageRevoked(AvillaEvent):
    message: Selector
    operator: Selector

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[MessageRevoked]):
            return await super().catch(interface)
