from __future__ import annotations

from graia.amnesia.message import MessageChain

from avilla.core.abstract.trait import Fn, Trait
from avilla.core.utilles.selector import Selector


# MessageFetch => rs.pull(Message, target=...)


class MessageSend(Trait):
    @Fn.bound
    async def send(self, message: MessageChain, *, reply: Selector | None = None) -> Selector:
        ...


class MessageRevoke(Trait):
    @Fn.bound
    async def revoke(self) -> None:
        ...


class MessageEdit(Trait):
    @Fn
    async def edit(self, message: Selector, content: MessageChain) -> None:
        ...
