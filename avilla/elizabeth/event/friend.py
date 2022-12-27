from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.message import __message_chain_class__
from pyparsing import Any

from avilla.core.context import Context
from avilla.core.event import MetadataModified, MetadataModify
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder
from avilla.spec.core.profile.metadata import Nick

if TYPE_CHECKING:
    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


event = EventParserRecorder["ElizabethProtocol", "ElizabethAccount"]


@event("FriendNickChangedEvent")
async def friend_nick_changed(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    friend = Selector().land(protocol.land).friend(str(raw["friend"]["id"]))
    context = Context(account, friend, friend, friend, account.to_selector())
    return (
        MetadataModified(
            context, friend, [MetadataModify(Nick.of(friend), "name", "set", raw["from"], raw["to"])], friend
        ),
        context,
    )
