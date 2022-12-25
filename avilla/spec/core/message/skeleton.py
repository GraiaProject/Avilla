from __future__ import annotations

from graia.amnesia.message import __message_chain_class__

from avilla.core.selector import Selector
from avilla.core.trait import Fn, Trait

# MessageFetch => rs.pull(Message, target=...)


class MessageSend(Trait):
    @Fn.bound_entity
    async def send(self, message: __message_chain_class__, *, reply: Selector | None = None) -> Selector:
        ...


class MessageRevoke(Trait):
    @Fn.bound_entity
    async def revoke(self) -> None:
        ...


class MessageEdit(Trait):
    @Fn
    async def edit(self, message: Selector, content: __message_chain_class__) -> None:
        ...
