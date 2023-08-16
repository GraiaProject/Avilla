from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from nonebot.adapters import Bot as BaseBot

from avilla.core.account import BaseAccount
from avilla.core.elements import Notice
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

        context = event.origin_event.context
        staff = self.service.staff.ext(context.get_staff_components())
        translated_message = await staff.deserialize_onebot_message(message)

        if reply_message and isinstance(event.origin_event, MessageReceived):
            reply = event.origin_event.message.sender
        else:
            reply = None

        if at_sender:
            translated_message.content = [Notice(context.client), *translated_message.content]

        sent_message = await context.scene.send_message(translated_message, reply=reply)
        return {"message_id": json.dumps({**sent_message.pattern})}
