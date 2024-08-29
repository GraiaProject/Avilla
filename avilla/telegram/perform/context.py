from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.builtins.capability import CoreCapability
from avilla.core.context import Context
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramContextPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::context"

    @m.entity(CoreCapability.get_context, target="land.chat")
    @m.entity(CoreCapability.get_context, target="land.chat.thread")
    def get_context_from_chat(self, target: Selector, *, via: Selector | None = None):
        is_group = int(target["chat"]) < 0  # some magic? works for me, but not mentioned in api docs tho.
        return Context(
            self.account,
            target.into("::chat"),
            target,
            target,
            target.member(self.account.route["account"]) if is_group else self.account.route,
        )

    @m.entity(CoreCapability.get_context, target="land.chat.member")
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::chat"),
            target.into("::chat"),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @m.entity(CoreCapability.get_context, target="land.chat.thread.member")
    def get_context_from_thread_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into("::thread"),
            target.into("::thread"),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @m.entity(CoreCapability.guild, target="land.chat")
    @m.entity(CoreCapability.guild, target="land.chat.member")
    @m.entity(CoreCapability.guild, target="land.chat.thread.member")
    def guild_from_chat(self, target: Selector):
        return target["chat"]

    @m.entity(CoreCapability.user, target="land.chat")
    @m.entity(CoreCapability.user, target="land.chat.member")
    @m.entity(CoreCapability.user, target="land.chat.thread.member")
    def user_from_chat(self, target: Selector):
        return target.last_value
