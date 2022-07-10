from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core.account import AccountSelector
from avilla.core.event.message import MessageReceived
from avilla.core.message import Message
from avilla.core.utilles.event_parser import AbstractEventParser, event
from avilla.core.utilles.selector import Selector

if TYPE_CHECKING:
    from .protocol import ElizabethProtocol


@dataclass
class _Source:
    id: int
    time: int


@dataclass
class _Quote:
    id: int
    group_id: int
    sender_id: int
    target_id: int
    origin: list


class ElizabethEventParser(AbstractEventParser["ElizabethProtocol"]):
    def get_event_type(self, raw: dict) -> str:
        return raw["type"]

    @event("GroupMessage")
    async def group_message(self, protocol: ElizabethProtocol, account: AccountSelector, raw: dict):
        message_chain = raw["messageChain"]
        source = None
        quote = None
        for i in message_chain:
            if i["type"] == "Source":
                source = _Source(i["id"], i["time"])
            elif i["type"] == "Quote":
                quote = _Quote(i["id"], i["groupId"], i["senderId"], i["targetId"], i["origin"])
        if source is None:
            raise ValueError("Source not found.")
        return MessageReceived(
            message=Message(
                id=str(source.id),
                mainline=Selector().land(protocol.land.name).group(str(raw["sender"]["group"]["id"])),
                sender=Selector()
                .land(protocol.land.name)
                .group(str(raw["sender"]["group"]["id"]))
                .member(str(raw["sender"]["id"])),
                content=MessageChain(await protocol.message_deserializer.parse_sentence(protocol, message_chain)),
                time=datetime.fromtimestamp(source.time),
                reply=Selector()
                .land(protocol.land.name)
                .group(str(raw["sender"]["group"]["id"]))
                .message(str(quote.id))
                if quote is not None
                else None,
            ),
            account=account,
        )
