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
from avilla.spec.core.profile.metadata import Nick, Summary
from avilla.spec.core.profile.skeleton import NickTrait

if TYPE_CHECKING:
    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


event = EventParserRecorder["ElizabethProtocol", "ElizabethAccount"]


@event("MemberJoinEvent")
async def member_join(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    new_member = group.member(str(raw["member"]["id"]))
    if raw["inviter"] is not None:
        inviter = group.member(raw["inviter"]["id"])
    else:
        inviter = None
    selft = group.member(account.id)
    context = Context(account, new_member, group, group, selft, [inviter] if inviter is not None else None)
    return RelationshipCreated(context), context


@event("MemberLeaveEventKick")
async def member_leave_kick(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    member = group.member(str(raw["member"]["id"]))
    selft = group.member(account.id)
    if raw["operator"] is None:
        operator = selft
    else:
        operator = group.member(str(raw["operator"]["id"]))
    context = Context(account, operator, member, group, selft)
    return RelationshipDestroyed(context, False), context


@event("MemberLeaveEventQuit")
async def member_leave_quit(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    member = group.member(str(raw["member"]["id"]))
    selft = group.member(account.id)
    context = Context(account, member, member, group, selft)
    return RelationshipDestroyed(context, True), context


@event("MemberCardChangeEvent")
async def member_card_change(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    member = group.member(str(raw["member"]["id"]))
    selft = group.member(account.id)
    if raw["operator"] is None:
        operator = selft
    else:
        operator = group.member(str(raw["operator"]["id"]))
    context = Context(account, operator, member, group, selft)
    return (
        MetadataModified(
            context=context,
            endpoint=member,
            modifies=[
                Op(
                    NickTrait.set_nickname,
                    {Nick.of(member): [Update(Nick.inh(lambda x: x.nickname), raw["current"], raw["origin"])]},
                )
            ],
            client=operator,
        ),
        context,
    )


@event("MemberSpecialTitleChangeEvent")
async def member_special_title_change(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw["group"]["id"]))
    member = group.member(str(raw["member"]["id"]))
    selft = group.member(account.id)
    group_ctx = await account.get_context(group)
    async for mem in group_ctx.query(f"group({raw['group']['id']}).member"):
        mem_priv_info = await group_ctx.pull(Privilege >> Summary, mem)
        if mem_priv_info.name == "group_owner":
            operator = mem
            break
    else:
        logger.warning("cannot found group owner for member special title changed event")
        operator = account.to_selector()
    context = Context(account, operator, member, group, selft)
    return (
        MetadataModified(
            context=context,
            endpoint=member,
            client=operator,
            modifies=[
                Op(
                    NickTrait.set_badge,
                    {Nick.of(member): [Update(Nick.inh(lambda x: x.badge), raw["current"], raw["origin"])]},
                )
            ],
        ),
        context,
    )


@event("MemberPermissionChangeEvent")
async def member_perm_changed_change(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw['member']["group"]["id"]))
    member = group.member(str(raw["member"]["id"]))
    selft = group.member(account.id)
    print("1")
    member_ctx = await account.get_context(member)
    print("2", raw, member_ctx.__dict__)
    try:
        async for mem in member_ctx.query(f"group({raw['member']['group']['id']}).member"):
            print("2222")
            mem_priv_info = await member_ctx.pull(Privilege >> Summary, mem)
            if mem_priv_info.name == "group_owner":
                operator = mem
                break
        else:
            logger.warning("cannot found group owner for member special title changed event")
            operator = account.to_selector()
    except:
        import traceback
        traceback.print_exc()
        raise
    print("3")
    context = Context(account, operator, member, group, selft)
    if privilege_level[raw["current"]] > privilege_level[raw["origin"]]:
        past, present = False, True
        op = PrivilegeTrait.upgrade
    else:
        past, present = True, False
        op = PrivilegeTrait.downgrade
    context._collect_metadatas(selft, Privilege(present, present, None))
    return (
        MetadataModified(
            context=context,
            endpoint=member,
            client=operator,
            modifies=[Op(op, {Privilege.of(member): [Update(Privilege.inh(lambda x: x.available), present, past)]})],
        ),
        context,
    )


@event("MemberMuteEvent")
async def member_mute_change(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(raw["member"]["group"]["id"])
    target = group.member(str(raw["member"]["id"]))
    selft = group.member(account.id)
    if raw["operator"] is None:
        operator = selft
    else:
        operator = group.member(str(raw["operator"]["id"]))
    context = Context(account, operator, selft, group, selft)
    context._collect_metadatas(
        target,
        MuteInfo(True, timedelta(seconds=raw["durationSeconds"]), datetime.now()),
    )
    context._collect_metadatas(operator, Privilege(True, False))
    return (
        MetadataModified(
            context=context,
            endpoint=selft,
            client=operator,
            modifies=[
                Op(
                    MuteTrait.mute,
                    {
                        MuteInfo.of(target): [
                            Bind(MuteInfo.inh(lambda x: x.muted), True),
                            Bind(MuteInfo.inh(lambda x: x.duration), timedelta(seconds=raw["durationSeconds"])),
                            Bind(MuteInfo.inh(lambda x: x.time), datetime.now()),
                        ]
                    },
                )
            ],
        ),
        context,
    )


@event("MemberUnmuteEvent")
async def member_unmute_change(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(raw["member"]["group"]["id"])
    target = group.member(str(raw["member"]["id"]))
    selft = group.member(account.id)
    if raw["operator"] is None:
        operator = selft
    else:
        operator = group.member(str(raw["operator"]["id"]))
    context = Context(account, operator, selft, group, selft)
    context._collect_metadatas(operator, Privilege(True, False))
    return (
        MetadataModified(
            context=context,
            endpoint=selft,
            client=operator,
            modifies=[
                Op(
                    MuteTrait.mute,
                    {
                        MuteInfo.of(target): [
                            Unbind(MuteInfo.inh(lambda x: x.muted)),
                            Unbind(MuteInfo.inh(lambda x: x.duration)),
                            Unbind(MuteInfo.inh(lambda x: x.time)),
                        ]
                    },
                )
            ],
        ),
        context,
    )
