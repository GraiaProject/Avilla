from __future__ import annotations

from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.standard.core.message import MessageReceived

from ...descriptor.event import NoneEventTranslate
from ...perform.base import NoneBridgePerform
from ...reference.event import GroupMessageEvent, PrivateMessageEvent
from ...reference.event import Sender as NonebotSender
from ...reference.message import Message as NonebotMessage
from ...reference.message import MessageSegment as NonebotMessageSegment


class MessageEventTranslater((m := ContextCollector())._, NoneBridgePerform):
    @NoneEventTranslate.collect(m, MessageReceived)
    async def message_received(self, event: MessageReceived):
        message = NonebotMessage(
            [
                NonebotMessageSegment(type=i["type"], data=i["data"])
                for i in await self.service.staff.serialize_onebot_message(event.message.content)
            ]
        )
        if event.context.scene.follows("::group"):
            return GroupMessageEvent(
                origin_event=event,
                time=int(event.time.timestamp()),
                self_id=int(event.context.account.route["account"]),
                post_type="message",
                message_type="group",
                sub_type="normal",
                message_id=int(event.message.id),
                message=message,
                group_id=int(event.context.scene["group"]),
                user_id=int(event.context.client["member"]),
                original_message=message,
                raw_message=str(event.message.content),
                font=0,
                sender=NonebotSender(
                    user_id=int(event.context.client["member"]),
                ),
            )
        elif event.context.scene.follows("land(qq).friend"):
            return PrivateMessageEvent(
                origin_event=event,
                time=int(event.time.timestamp()),
                self_id=int(event.context.account.route["account"]),
                post_type="message",
                message_type="private",
                sub_type="normal",
                message_id=int(event.message.id),
                message=message,
                user_id=int(event.context.client["friend"]),
                original_message=message,
                raw_message=str(event.message.content),
                font=0,
                sender=NonebotSender(
                    user_id=int(event.context.client["friend"]),
                ),
            )
        elif event.context.scene.follows("land(console).user(console)"):
            return PrivateMessageEvent(
                origin_event=event,
                time=int(event.time.timestamp()),
                self_id=1919810,
                post_type="message",
                message_type="private",
                sub_type="normal",
                # message_id=int(event.message.id),
                message_id=233333333,
                message=message,
                user_id=114514,
                original_message=message,
                raw_message=str(event.message.content),
                font=0,
                sender=NonebotSender(
                    user_id=114514,
                ),
            )

        return
