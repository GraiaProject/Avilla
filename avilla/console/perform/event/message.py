from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived

from avilla.console.frontend.info import Event, MessageEvent

if TYPE_CHECKING:
    from ...account import ConsoleAccount
    from ...protocol import ConsoleProtocol

ConsoleEventParse = EventParse[Event]


class ConsoleEventMessagePerform(
    (m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._
):
    m.post_applying = True

    @ConsoleEventParse.collect(m, "console.message")
    async def console_message(self, raw_event: Event):
        if TYPE_CHECKING:
            assert isinstance(raw_event, MessageEvent)
        message = await Staff(
            self.account, element_typer=lambda e: type(e).__name__
        ).deserialize_message(raw_event.message.content)
        console = (
            Selector().land(self.account.route["land"]).console(str(raw_event.user.id))
        )
        context = Context(
            account=self.account,
            client=console,
            endpoint=console,
            scene=console,
            selft=self.account.route,
        )
        return MessageReceived(
            context,
            Message(
                id=raw_event.msg_id,
                scene=console,
                sender=console,
                content=message,
                time=datetime.fromtimestamp(raw_event.time.timestamp()),
            ),
        )
