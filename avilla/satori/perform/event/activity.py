from __future__ import annotations

from flywheel import scoped_collect
from satori.model import ChannelType

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.satori.bases import InstanceOfAccount
from avilla.satori.capability import SatoriCapability
from avilla.satori.model import ButtonInteractionEvent
from avilla.standard.core.activity import ActivityAvailable


class SatoriEventActivityPerform(m := scoped_collect.globals().target, InstanceOfAccount, static=True):
    @m.impl(SatoriCapability.event_callback, raw_event="interaction/button")
    async def button_interaction(self, event: ButtonInteractionEvent):
        account = self.account
        if event.channel.type == ChannelType.DIRECT:
            private = Selector().land(account.route["land"]).private(event.channel.id)
            user = private.user(event.user.id)  # type: ignore
            context = Context(
                account,
                user,
                account.route,
                user,
                account.route,
            )
            activity = private.button(event.button.id)  # type: ignore
        else:
            public = Selector().land(account.route["land"]).public(event.guild.id if event.guild else event.channel.id)
            channel = public.channel(event.channel.id)
            member = channel.member(event.member.user.id if event.member and event.member.user else event.user.id)
            context = Context(
                account,
                member,
                channel,
                channel,
                channel.member(account.route["account"]),
            )
            activity = channel.button(event.button.id)  # type: ignore
        return ActivityAvailable(context, "button_interaction", context.scene, activity)
