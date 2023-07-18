from __future__ import annotations

from collections import ChainMap
from typing import TYPE_CHECKING, Any

from nonebot.adapters import Bot as BaseBot

from avilla.core.account import BaseAccount
from avilla.core.ryanvk.staff import Staff
from avilla.standard.core.message import MessageReceived

from .reference.event import Event
from .reference.message import Message, MessageSegment

if TYPE_CHECKING:
    from .service import NoneBridgeService


class NoneBridgeBot(BaseBot):
    # 作为面向 nb 侧的 account 代理.

    def __init__(self, service: NoneBridgeService, account: BaseAccount):
        self.service = service
        self.adapter = service.adapter
        self.account = account
        self.self_id = "avilla.nonebridge"

    async def send(
        self,
        event: Event,
        message: str | Message | MessageSegment,
        *,
        at_sender: bool = False,
        reply_message: bool = False,
        **kwargs: Any,
    ) -> Any:
        if isinstance(message, str):
            message = Message(message)
        elif isinstance(message, MessageSegment):
            message = Message([message])

        staff = Staff(
            {
                "avilla": self.service.avilla,
                # TODO
            },
            ChainMap(self.service.isolate.artifacts),
        )
        translated_message = await staff.deserialize_message([{"type": i.type, "data": i.data} for i in message])

        if reply_message and isinstance(event.origin_event, MessageReceived):
            reply = event.origin_event.message.sender
        else:
            reply = None
        sent_message = await event.origin_event.context.scene.send_message(translated_message, reply=reply)
        return {"message_id": sent_message["message"]}
