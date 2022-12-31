from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from loguru import logger

from avilla.core.context import Context
from avilla.core.event import (
    Bind,
    MetadataModified,
    Op,
    RelationshipCreated,
    RelationshipDestroyed,
    Unbind,
    Update,
)
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder
from avilla.elizabeth.const import privilege_level
from avilla.spec.core.privilege.metadata import MuteInfo, Privilege
from avilla.spec.core.privilege.skeleton import MuteTrait, PrivilegeTrait
from avilla.spec.core.profile.metadata import Summary

if TYPE_CHECKING:
    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


event = EventParserRecorder["ElizabethProtocol", "ElizabethAccount"]


@event("BotGroupPermissionChangeEvent")
async def account_permission_change(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
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
    if privilege_level[raw["current"]] > privilege_level[raw["origin"]]:
        past, present = False, True
        op = PrivilegeTrait.upgrade
    else:
        past, present = True, False
        op = PrivilegeTrait.downgrade
    context._collect_metadatas(account_member, Privilege(present, present, None))
    return (
        MetadataModified(
            context=context,
            endpoint=context.endpoint,
            client=operator,
            modifies=[
                Op(op, {Privilege.of(account_member): [Update(Privilege.inh(lambda x: x.available), present, past)]})
            ],
        ),
        context,
    )


@event("BotMuteEvent")
async def account_muted(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(raw["operator"]["group"]["id"])
    operator = group.member(raw["operator"]["id"])
    account_member = group.member(account.id)
    context = Context(account, operator, account_member, group, account_member)
    context._collect_metadatas(
        account_member,
        MuteInfo(True, timedelta(seconds=raw["duration"]), datetime.now()),
    )
    context._collect_metadatas(operator, Privilege(True, False))
    return (
        MetadataModified(
            context=context,
            endpoint=account_member,
            client=operator,
            modifies=[
                Op(
                    MuteTrait.mute,
                    {
                        MuteInfo.of(account_member): [
                            Bind(MuteInfo.inh(lambda x: x.muted), True),
                            Bind(MuteInfo.inh(lambda x: x.duration), timedelta(seconds=raw["duration"])),
                            Bind(MuteInfo.inh(lambda x: x.time), datetime.now()),
                        ]
                    },
                )
            ],
        ),
        context,
    )


@event("BotUnmuteEvent")
async def account_unmuted(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(raw["operator"]["group"]["id"])
    operator = group.member(raw["operator"]["id"])
    account_member = group.member(account.id)
    context = Context(account, operator, account_member, group, account_member)
    context._collect_metadatas(
        account_member,
        MuteInfo(True, timedelta(seconds=raw["duration"]), datetime.now()),
    )
    context._collect_metadatas(operator, Privilege(True, False))
    return (
        MetadataModified(
            context=context,
            endpoint=account_member,
            client=operator,
            modifies=[
                Op(
                    MuteTrait.mute,
                    {
                        MuteInfo.of(account_member): [
                            Update(MuteInfo.inh(lambda x: x.muted), True, False),
                            Unbind(MuteInfo.inh(lambda x: x.duration)),
                            Unbind(MuteInfo.inh(lambda x: x.time)),
                        ]
                    },
                )
            ],
        ),
        context,
    )


@event("BotJoinGroupEvent")
async def account_join_group(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    if raw["inviter"] is not None:
        inviter = group.member(raw["inviter"]["id"])
    else:
        inviter = None
    account_member = group.member(account.id)
    context = Context(
        account, account_member, account_member, group, account_member, [inviter] if inviter is not None else None
    )
    return RelationshipCreated(context), context


@event("BotLeaveGroupEventActive")
async def account_leave_group_active(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    account_member = group.member(account.id)
    context = Context(account, account_member, account_member, group, account_member)
    return RelationshipDestroyed(context, True), context


@event("BotLeaveGroupEventKick")
async def account_leave_group_kick(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    account_member = group.member(account.id)
    operator = group.member(raw["operator"]["id"])
    context = Context(account, operator, account_member, group, account_member)
    return RelationshipDestroyed(context, False), context


@event("BotLeaveGroupEventDisband")
async def account_leave_group_disband(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    account_member = group.member(account.id)
    operator = group.member(raw["operator"]["id"])
    context = Context(account, operator, account_member, group, account_member)
    return RelationshipDestroyed(context, False, True), context
