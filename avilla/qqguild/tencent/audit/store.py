import asyncio
from typing import TYPE_CHECKING, Dict, Optional
from weakref import finalize

if TYPE_CHECKING:
    from .event import MessageAudited


class AuditResultStore:
    def __init__(self) -> None:
        self._futures: Dict[str, asyncio.Future] = {}
        finalize(self, self._futures.clear)

    def add_result(self, result: "MessageAudited"):
        audit = result.audit.id
        if future := self._futures.get(audit):
            future.set_result(result)

    async def fetch(self, audit: str, timeout: float = 30) -> Optional["MessageAudited"]:
        future = asyncio.get_event_loop().create_future()
        self._futures[audit] = future
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            del self._futures[audit]


audit_result = AuditResultStore()
