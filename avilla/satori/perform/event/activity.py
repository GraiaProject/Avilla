from __future__ import annotations
from typing import TYPE_CHECKING

from satori.model import ChannelType, Event
from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.satori.capability import SatoriCapability
from avilla.satori.collector.connection import ConnectionCollector
from avilla.standard.core.activity import ActivityAvailable
from avilla.satori.model import OuterEvent


class SatoriEventActivityPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/satori::event"
    m.identify = "activity"

    @m.entity(SatoriCapability.event_callback, raw_event="interaction/button")
    async def button_interaction(self, raw_event: Event):
        account = self.protocol.service._accounts[self.connection.identity]
        if not raw_event.channel:
            return
        if TYPE_CHECKING:
            assert isinstance(raw_event, OuterEvent)
        if raw_event.channel.type == ChannelType.DIRECT:
            private = Selector().land(account.route["land"]).private(raw_event.channel.id)
            user = private.user(raw_event.user.id) # type: ignore
            context = Context(
                account,
                user,
                account.route,
                user,
                account.route,
            )
            activity = private.button(raw_event.button.id)  # type: ignore
        else:
            public = (
                Selector()
                .land(account.route["land"])
                .public(raw_event.guild.id if raw_event.guild else raw_event.channel.id)
            )
            channel = public.channel(raw_event.channel.id)
            member = channel.member(
                raw_event.member.user.id if raw_event.member and raw_event.member.user else raw_event.user.id
            )
            context = Context(
                account,
                member,
                channel,
                channel,
                channel.member(account.route["account"]),
            )
            activity = channel.button(raw_event.button.id)  # type: ignore
        return ActivityAvailable(context, "button_interaction", context.scene, activity)
