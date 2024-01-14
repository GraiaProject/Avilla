from __future__ import annotations

from datetime import datetime

from avilla.core.context import Context
from avilla.core.request import Request
from avilla.core.selector import Selector
from avilla.elizabeth.capability import ElizabethCapability
from avilla.elizabeth.collector.connection import ConnectionCollector
from avilla.elizabeth.const import LAND
from avilla.standard.core.profile.metadata import Nick, Summary
from avilla.standard.core.request import RequestReceived


class ElizabethEventRequestPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/elizabeth::event"
    m.identify = "request"

    @m.entity(ElizabethCapability.event_callback, raw_event="MemberJoinRequestEvent")
    async def member_join_request(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["groupId"]))
        sender = land.contact(str(raw_event["fromId"]))
        context = Context(
            account,
            sender,
            group,
            group,
            account_route,
            mediums=[group.member(str(raw_event["invitorId"]))] if raw_event.get("invitorId") else None,
        )
        request = Request(
            f"{raw_event['eventId']}/{raw_event['fromId']}",
            LAND,
            group,
            sender,
            account,
            datetime.now(),
            request_type="elizabeth::member_join",
            message=raw_event.get("message"),
        )
        context._collect_metadatas(
            group,
            Nick(raw_event["groupName"], raw_event["groupName"], None),
            Summary(raw_event["groupName"], None),
        )
        context._collect_metadatas(
            sender,
            Nick(raw_event["nick"], raw_event["nick"], None),
            Summary(raw_event["nick"], None),
        )
        return RequestReceived(context, request)

    @m.entity(ElizabethCapability.event_callback, raw_event="NewFriendRequestEvent")
    async def new_friend_request(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        sender = land.group(str(raw_event["groupId"])).contact(str(raw_event["fromId"]))
        context = Context(
            account,
            sender,
            account_route,
            sender,
            account_route,
            mediums=[land.group(str(raw_event["groupId"]))] if raw_event.get("groupId") else None,
        )
        request = Request(
            f"{raw_event['eventId']}",
            LAND,
            sender,
            sender,
            account,
            datetime.now(),
            request_type="elizabeth::new_friend",
            message=raw_event.get("message"),
        )
        context._collect_metadatas(
            sender,
            Nick(raw_event["nick"], raw_event["nick"], None),
            Summary(raw_event["nick"], None),
        )
        return RequestReceived(context, request)

    @m.entity(ElizabethCapability.event_callback, raw_event="BotInvitedJoinGroupRequestEvent")
    async def bot_invited_join_group_request(self, raw_event: dict):
        account_route = Selector().land("qq").account(str(self.connection.account_id))
        account = self.protocol.avilla.accounts[account_route].account
        land = Selector().land("qq")
        group = land.group(str(raw_event["groupId"]))
        member = group.member(str(raw_event["fromId"]))
        context = Context(
            account,
            member,
            account_route,
            member,
            account_route,
        )
        request = Request(
            f"{raw_event['eventId']}",
            LAND,
            member,
            member,
            account,
            datetime.now(),
            request_type="elizabeth::invited_join_group",
            message=raw_event.get("message"),
        )
        context._collect_metadatas(
            member,
            Nick(raw_event["nick"], raw_event["nick"], None),
            Summary(raw_event["nick"], None),
        )
        context._collect_metadatas(
            group,
            Nick(raw_event["groupName"], raw_event["groupName"], None),
            Summary(raw_event["groupName"], None),
        )
        return RequestReceived(context, request)
