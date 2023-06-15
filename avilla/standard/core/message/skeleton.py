from __future__ import annotations

from graia.amnesia.message import MessageChain

from avilla.core.selector import Selector
from avilla.core.ryanvk import Capability, TargetFn, Fn

# MessageFetch => rs.pull(Message, target=...)


class MessageSend(Capability):
    @TargetFn
    async def send(self, target: Selector, message: MessageChain, *, reply: Selector | None = None) -> Selector:
        ...


class MessageRevoke(Capability):
    @TargetFn
    async def revoke(self, target: Selector) -> None:
        ...


class MessageEdit(Capability):
    @Fn
    async def edit(self, message: Selector, content: MessageChain) -> None:
        ...
