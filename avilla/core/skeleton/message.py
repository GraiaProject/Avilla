from __future__ import annotations

from graia.amnesia.message import MessageChain

from avilla.core.trait import DirectFn, Fn, Trait
from avilla.core.utilles.selector import Selector


class MessageTrait(Trait):
    @DirectFn
    async def send(self, message: MessageChain, *, reply: Selector | None = None) -> Selector:
        ...

    @Fn
    async def revoke(self, message: Selector) -> None:
        ...

    @Fn
    async def edit(self, message: Selector, content: MessageChain) -> None:
        ...

    # MessageFetch => rs.pull(Message, target=...)
