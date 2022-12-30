from __future__ import annotations

from typing import TYPE_CHECKING, Any

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder
from avilla.spec.core.application.event import AccountAvailable, AccountUnavailable

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent

    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


event = EventParserRecorder["ElizabethProtocol", "ElizabethAccount"]


@event("BotOnlineEvent")
async def bot_online(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    return AccountAvailable(protocol.avilla, account), Context(
        account, account.to_selector(), account.to_selector(), Selector().land(protocol.land), account.to_selector()
    )


@event("BotOfflineEventActive")
@event("BotOfflineEventForce")
@event("BotOfflineEventDropped")
async def bot_offline(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    return AccountUnavailable(protocol.avilla, account), Context(
        account, account.to_selector(), account.to_selector(), Selector().land(protocol.land), account.to_selector()
    )


@event("BotReloginEvent")
async def bot_relogin(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    return AccountUnavailable(protocol.avilla, account), Context(
        account, account.to_selector(), account.to_selector(), Selector().land(protocol.land), account.to_selector()
    )
