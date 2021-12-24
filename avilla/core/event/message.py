from datetime import datetime
from typing import Literal, Union

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from pydantic import Field

from avilla.core.context import ctx_relationship
from avilla.core.message import Message
from avilla.core.selectors import entity, mainline

from . import AvillaEvent


class MessageEvent(AvillaEvent):
    message: Message

    current: entity
    time: datetime

    def __init__(
        self,
        message: Message,
        current: entity,
        time: datetime = None,
    ) -> None:
        self.message = message
        self.current = current
        self.time = time or datetime.now()

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass
