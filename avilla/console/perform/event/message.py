from __future__ import annotations

from secrets import token_hex
from typing import TYPE_CHECKING

from nonechat.info import MessageEvent

from avilla.console.capability import ConsoleCapability
from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from avilla.console.account import ConsoleAccount  # noqa
    from avilla.console.protocol import ConsoleProtocol  # noqa


class ConsoleEventMessagePerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.namespace = "avilla.protocol/console::event/message"

    @m.entity(ConsoleCapability.event_callback, event=MessageEvent)
    async def console_message(self, event: MessageEvent):
        console = Selector().land(self.account.route["land"]).user(str(event.user.id))
        message = MessageChain(
            [await self.staff.call_fn(ConsoleCapability.deserialize_element, i) for i in event.message.content]
        )
        context = Context(
            account=self.account,
            client=console,
            endpoint=self.account.route,
            scene=console,
            selft=self.account.route,
        )
        return MessageReceived(
            context,
            Message(
                id=token_hex(16),
                scene=console,
                sender=console,
                content=message,
                time=event.time,
            ),
        )
