from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.core.trait.context import ContextSourceRecorder

if TYPE_CHECKING:
    from ..account import ElizabethAccount

_source_record = ContextSourceRecorder["ElizabethAccount"]


@_source_record("friend")
async def get_friend_context(account: ElizabethAccount, target: Selector, *, via: Selector | None = None) -> Context:
    friend = target.land(account.land)
    return Context(account, account.to_selector(), friend, friend, account.to_selector(), [via] if via else [])


@_source_record("group")
async def get_group_context(account: ElizabethAccount, target: Selector, *, via: Selector | None = None) -> Context:
    group = target.land(account.land)
    selft = group.member(account.id)
    return Context(account, selft, group, group, selft, [via] if via else [])


@_source_record("group.member")
async def get_group_member_context(
    account: ElizabethAccount, target: Selector, *, via: Selector | None = None
) -> Context:
    group = Selector().land(account.land).group(target["group"])
    selft = group.member(account.id)
    return Context(account, selft, target.land(account.land), group, selft, [via] if via else [])
