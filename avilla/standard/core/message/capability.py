from __future__ import annotations

from graia.amnesia.message import MessageChain

from avilla.core.ryanvk import Capability, Fn, TargetOverload
from avilla.core.selector import Selector

# MessageFetch => rs.pull(Message, target=...)


class MessageSend(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def send(self, target: Selector, message: MessageChain, *, reply: Selector | None = None) -> Selector:
        ...


class MessageRevoke(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def revoke(self, target: Selector) -> None:
        ...


class MessageEdit(Capability):
    @Fn.complex({TargetOverload(): ["target"]})
    async def edit(self, target: Selector, content: MessageChain) -> None:
        ...
