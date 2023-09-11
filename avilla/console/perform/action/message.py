from __future__ import annotations

from datetime import datetime
from secrets import token_hex
from typing import TYPE_CHECKING

from loguru import logger
from nonechat.info import Robot
from nonechat.message import ConsoleMessage

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend, MessageSent
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from avilla.console.account import ConsoleAccount  # noqa
    from avilla.console.protocol import ConsoleProtocol  # noqa


class ConsoleMessageActionPerform((m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.post_applying = True
    targets = ["land.user"]

    @m.entity(MessageSend.send, "land.user")
    async def send_console_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(self.protocol, ConsoleProtocol)
        serialized_msg = ConsoleMessage(await Staff.focus(self.account).serialize_message(message))

        await self.account.client.call("send_msg", {"message": serialized_msg, "info": Robot(self.protocol.name)})
        context = Context(
            account=self.account,
            client=self.account.route,
            endpoint=target,
            scene=target,
            selft=self.account.route,
        )
        event = MessageSent(
            context,
            Message(
                id=token_hex(16),
                scene=target,
                sender=self.account.route,
                content=message,
                time=datetime.now(),
            ),
            self.account,
        )
        self.protocol.post_event(event)
        return Selector().land(self.account.route["land"]).message(event.message.id)
