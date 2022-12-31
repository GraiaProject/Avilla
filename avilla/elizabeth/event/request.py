from __future__ import annotations
from datetime import datetime

from typing import TYPE_CHECKING, Any

from loguru import logger
from avilla.core.request import Request
from avilla.spec.core.activity.event import ActivityTrigged
from avilla.spec.core.message.event import MessageRevoked

from graia.amnesia.message import __message_chain_class__

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder
from avilla.spec.core.message import MessageReceived
from avilla.core.event import Bind, MetadataModified, Op, RelationshipCreated, RelationshipDestroyed, Unbind, Update
from avilla.spec.core.privilege.metadata import MuteInfo, Privilege
from avilla.spec.core.privilege.skeleton import MuteAllTrait, MuteTrait, PrivilegeTrait
from avilla.spec.core.profile.metadata import Nick, Summary
from avilla.spec.core.profile.skeleton import NickTrait
from avilla.elizabeth.const import privilege_level
from avilla.spec.core.request.event import RequestReceived

if TYPE_CHECKING:
    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol


event = EventParserRecorder["ElizabethProtocol", "ElizabethAccount"]


@event("NewFriendRequestEvent")
async def new_friend_req(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    request = Selector().land(protocol.land).friend_request(str(raw["eventId"]))
    friend_account = Selector().land(protocol.land).account(str(raw["fromId"]))
    context = Context(account, friend_account, request, Selector().land(protocol.land), account.to_selector())
    # TODO: metadata collect
    return (
        RequestReceived(
            context,
            Request(
                str(raw["eventId"]),
                protocol.land,
                context.scene,
                friend_account,
                account,
                datetime.now(),
                "new_friend",
            ),
        ),
        context,
    )

@event("MemberJoinRequestEvent")
async def member_join_req(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    request = Selector().land(protocol.land).group(str(raw['groupId'])).member_join_request(str(raw["eventId"]))
    member_account = Selector().land(protocol.land).account(str(raw["fromId"]))
    context = Context(account, member_account, request, Selector().land(protocol.land), account.to_selector())
    # TODO: metadata collect
    return (
        RequestReceived(
            context,
            Request(
                str(raw["eventId"]),
                protocol.land,
                context.scene,
                member_account,
                account,
                datetime.now(),
                "group.member_join",
            ),
        ),
        context,
    )

@event("BotInvitedJoinGroupRequestEvent")
async def invited_join_group(protocol: ElizabethProtocol, account: ElizabethAccount, raw: dict[str, Any]):
    group = Selector().land(protocol.land).group(str(raw['groupId']))
    request = Selector().land(protocol.land).group(str(raw['groupId'])).invite_join(str(raw["eventId"]))
    member_account = group.member(str(raw["fromId"]))
    context = Context(account, member_account, request, Selector().land(protocol.land), account.to_selector())
    # TODO: metadata collect
    return (
        RequestReceived(
            context,
            Request(
                str(raw["eventId"]),
                protocol.land,
                context.scene,
                member_account,
                account,
                datetime.now(),
                "group.invite_join",
            ),
        ),
        context,
    )