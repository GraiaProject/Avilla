from __future__ import annotations

from graia.amnesia.message import MessageChain

from avilla.core.abstract.trait import Fn, TBounded, Trait
from avilla.core.utilles.selector import Selector


# MessageFetch => rs.pull(Message, target=...)
class MessageSend(Trait[TBounded]):
    @Fn.bound
    async def send(self, message: MessageChain, *, reply: Selector | None = None) -> Selector:
        ...


class MessageRevoke(Trait[TBounded]):
    @Fn
    async def revoke(self, message: Selector) -> None:
        ...


class MessageEdit(Trait[TBounded]):
    @Fn
    async def edit(self, message: Selector, content: MessageChain) -> None:
        ...
