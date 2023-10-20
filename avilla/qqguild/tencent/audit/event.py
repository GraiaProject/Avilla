from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core.event import AvillaEvent

from .metadata import Audit

if TYPE_CHECKING:
    from graia.broadcast.interfaces.dispatcher import DispatcherInterface


@dataclass
class MessageAudited(AvillaEvent):
    audit: Audit

    class Dispatcher(AvillaEvent.Dispatcher):
        @classmethod
        async def catch(cls, interface: DispatcherInterface[MessageAudited]):
            if interface.annotation is Audit:
                return interface.event.audit
            return await AvillaEvent.Dispatcher.catch(interface)


@dataclass
class MessageAuditPass(MessageAudited):
    pass


@dataclass
class MessageAuditReject(MessageAudited):
    pass
