from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.spec.core.message import MessageRevoke
from avilla.spec.core.message.event import MessageReceived

from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull

if TYPE_CHECKING:
    from avilla.core.context import Context

    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol

with bounds("group.message"):

    @implement(MessageRevoke.revoke)
    async def revoke_group_message(cx: Context, message_selector: Selector):
        await cx.account.call(
            "recall",
            {
                "__method__": "update",
                "messageId": int(message_selector.last_value),
                "target": int(message_selector["group"]),
            },
        )

    @pull(Message)
    async def get_message_from_id(cx: Context, message_selector: Selector):
        if TYPE_CHECKING:
            assert isinstance(cx.account, ElizabethAccount)
            assert isinstance(cx.protocol, ElizabethProtocol)
        if cx.avilla.service.enabled_cache_message:
            result = cx.avilla.service.message_cache[cx.account.to_selector()].get(message_selector)
            if result is not None:
                return result
        result = await cx.account.call(
            "messageFromId",
            {
                "__method__": "fetch",
                "messageId": int(message_selector["message"]),
                "target": int(message_selector["group"]),
            },
        )
        event, event_context = await cx.protocol.parse_event(cx.account, result["data"])
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)
        cx.cache["meta"].update(event_context.cache["meta"])
        return event.message
