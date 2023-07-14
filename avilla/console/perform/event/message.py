from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.standard.core.message import MessageReceived
from avilla.console.frontend.info import MessageEvent
from avilla.console.staff import ConsoleStaff

from ...descriptor.event import ConsoleEventParse

if TYPE_CHECKING:
    ...


class ConsoleEventMessagePerform((m := AccountCollector())._):
    m.post_applying = True

    @ConsoleEventParse.collect(m, "console.message", MessageEvent)
    async def console_message(self, raw_event: MessageEvent):
        message = await ConsoleStaff(self.account).deserialize_message(raw_event.message)
        console = Selector().land(self.account.route["land"]).console(str(raw_event.user.id))
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
                id=str(raw_event.time.timestamp()),
                scene=console,
                sender=console,
                content=message,
                time=datetime.fromtimestamp(raw_event.time.timestamp())
            ),
        )

