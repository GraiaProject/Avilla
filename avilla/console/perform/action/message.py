from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend
from graia.amnesia.message import MessageChain
from loguru import logger

from ...frontend.info import Robot
from ...message import ConsoleMessage

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa


class ConsoleMessageActionPerform(
    (m := AccountCollector["ConsoleProtocol", "ConsoleAccount"]())._
):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.console")
    async def send_console_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(self.protocol, ConsoleProtocol)
        serialized_msg = ConsoleMessage(
            await Staff(self.account).serialize_message(message)
        )

        msg_id = await self.account.client.call(
            "send_msg", {"message": serialized_msg, "info": Robot(self.protocol.name)}
        )
        if not msg_id:
            raise RuntimeError(f"Failed to send message to console: {message}")
        logger.info(
            f"{self.account.route['land']}: [send]" f"[Console]" f" <- {str(message)!r}"
        )
        return Selector().land(self.account.route["land"]).message(msg_id)
