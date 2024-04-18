from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core.event import AvillaEvent

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface
    from avilla.core.selector import Selector

from .metadata import FileData

@dataclass
class FileReceived(AvillaEvent):
    file: Selector

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[FileReceived]):
            return await AvillaEvent.Dispatcher.catch(interface)

    async def get_filedatas(self) -> FileData:
        return await self.context.pull(FileData, self.file)
