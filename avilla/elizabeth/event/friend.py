from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avilla.spec.core.profile.metadata import Nick
from avilla.spec.core.profile.skeleton import NickCapability

from avilla.core.context import Context
from avilla.core.event import MetadataModified, Op, Update
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder

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
            context=context,
            endpoint=friend,
            client=friend,
            modifies=[
                Op(
                    NickCapability.set_name,
                    {
                        Nick.of(friend): [
                            Update(field=Nick.inh(lambda x: x.name), past=raw["from_name"], present=raw["to_name"])
                        ]
                    },
                )
            ],
        ),
        context,
    )
