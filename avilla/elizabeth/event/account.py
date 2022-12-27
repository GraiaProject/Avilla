from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from pyparsing import Any

from avilla.core.context import Context
from avilla.core.event import MetadataModified, MetadataModify
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder
from avilla.spec.core.privilege.metadata import Privilege
from avilla.spec.core.profile.metadata import Summary

if TYPE_CHECKING:
    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


event = EventParserRecorder["ElizabethProtocol", "ElizabethAccount"]

"""
@event("BotGroupPermissionChangeEvent")
async def account_permission_change(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().group(raw["group"]["id"])
    group_ctx = await account.get_context(group)
    async for mem in group_ctx.query(f"group({raw['group']['id']}).member"):
        mem_priv_info = await group_ctx.pull(Privilege >> Summary, mem)
        if mem_priv_info.name == "group_owner":
            operator = mem
            break
    else:
        logger.warning("cannot found group owner for permission changed event")
        operator = account.to_selector()
    account_member = group.member(account.id)
    context = Context(account, operator, account_member, group, account_member)
    return MetadataModified(
        context, context.endpoint, [MetadataModify(Privilege.of(account_member), "available", "")], operator
    )
"""