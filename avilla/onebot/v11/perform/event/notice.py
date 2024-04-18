from __future__ import annotations

from datetime import timedelta
from typing import cast

from loguru import logger

from avilla.core.context import Context
from avilla.core.event import (
    DirectSessionCreated,
    MetadataModified,
    ModifyDetail,
    SceneCreated,
    SceneDestroyed,
)
from avilla.core.selector import Selector
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.onebot.v11.collector.connection import ConnectionCollector
from avilla.standard.core.activity import ActivityTrigged
from avilla.standard.core.privilege import MuteInfo, Privilege
from avilla.standard.core.file import FileReceived
from avilla.standard.qq.event import PocketLuckyKingNoticed
from avilla.standard.qq.honor import Honor


class OneBot11EventNoticePerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/onebot11::event"
    m.identify = "notice"

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_admin.set")
    async def group_admin_set(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))

        # get operator(group owner)
        members = await self.connection.call("get_group_member_list", {"group": raw_event["group_id"]})
        members = cast("list[dict]", members)
        operator_id = next((d["id"] for d in members if d["role"] == "owner"), None)
        operator = group.member(str(operator_id)) if operator_id else group
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return MetadataModified(
            context,
            endpoint,
            Privilege,
            {
                Privilege.inh().available: ModifyDetail("update", True, False),
                Privilege.inh().effective: ModifyDetail("update", True, False),
            },
            operator=operator,
            scene=group,
        )

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_admin.unset")
    async def group_admin_unset(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))

        # get operator(group owner)
        members = await self.connection.call("get_group_member_list", {"group": raw_event["group_id"]})
        members = cast("list[dict]", members)
        operator_id = next((d["id"] for d in members if d["role"] == "owner"), None)
        operator = group.member(str(operator_id)) if operator_id else group
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return MetadataModified(
            context,
            endpoint,
            Privilege,
            {
                Privilege.inh().available: ModifyDetail("update", False, True),
                Privilege.inh().effective: ModifyDetail("update", False, True),
            },
            operator=operator,
            scene=group,
        )

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_decrease.leave")
    async def member_leave(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))
        operator = group.member(str(raw_event["operator_id"]))
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return SceneDestroyed(context, True, True)

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_decrease.kick")
    async def member_kick(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))
        operator = group.member(str(raw_event["operator_id"]))
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return SceneDestroyed(context, False, True)

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_decrease.kick_me")
    async def member_kick_me(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))
        operator = group.member(str(raw_event["operator_id"]))
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return SceneDestroyed(context, False, False)

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_increase.approve")
    async def member_increase_approve(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))
        operator = group.member(str(raw_event["operator_id"]))
        context = Context(
            account,
            operator,
            endpoint,
            group,
            group.member(str(self_id)),
        )
        return SceneCreated(context)

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_increase.invite")
    async def member_increase_invite(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))
        operator = group.member(str(raw_event["operator_id"]))
        context = Context(account, operator, endpoint, group, group.member(str(self_id)), mediums=[group])
        return SceneCreated(context)

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_ban.ban")
    async def member_muted(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))
        operator = group.member(str(raw_event["operator_id"]))
        context = Context(
            account,
            operator,
            endpoint,
            group,
            group.member(str(self_id)),
        )
        return MetadataModified(
            context,
            endpoint,
            MuteInfo,
            {
                MuteInfo.inh().muted: ModifyDetail("set", True),
                MuteInfo.inh().duration: ModifyDetail("set", timedelta(seconds=raw_event["duration"])),
            },
            operator=operator,
            scene=group,
        )

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_ban.lift_ban")
    async def member_unmuted(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land("qq").group(str(raw_event["group_id"]))
        endpoint = group.member(str(raw_event["user_id"]))
        operator = group.member(str(raw_event["operator_id"]))
        context = Context(
            account,
            operator,
            endpoint,
            group,
            group.member(str(self_id)),
        )
        return MetadataModified(
            context,
            endpoint,
            MuteInfo,
            {
                MuteInfo.inh().muted: ModifyDetail("clear"),
                MuteInfo.inh().duration: ModifyDetail("clear"),
            },
            operator=operator,
            scene=group,
        )

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.friend_add")
    async def friend_add(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        friend = Selector().land("qq").friend(str(raw_event["user_id"]))
        context = Context(account, friend, friend, friend, account.route)
        return DirectSessionCreated(context)

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.notify.poke")
    async def nudge_received(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return
        if "group_id" in raw_event:
            group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
            target = group.member(str(raw_event["target_id"]))
            operator = group.member(str(raw_event["user_id"]))
            context = Context(account, operator, target, group, group.member(str(self_id)))
            return ActivityTrigged(context, "nudge", group, target.nudge("_"), operator)
        else:
            friend = Selector().land(account.route["land"]).friend(str(raw_event["sender_id"]))
            selft = account.route
            context = Context(account, friend, selft, friend, selft)
            return ActivityTrigged(context, "nudge", friend, friend.nudge("_"), friend)

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.notify.lucky_king")
    async def lucky_king_received(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return

        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        target = group.member(str(raw_event["target_id"]))
        operator = group.member(str(raw_event["user_id"]))
        context = Context(account, operator, target, group, group.member(str(self_id)))
        return PocketLuckyKingNoticed(context)

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.notify.honor")
    async def honor(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return

        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        user = group.member(str(raw_event["user_id"]))
        context = Context(account, group, user, group, group.member(str(self_id)))
        return MetadataModified(
            context,
            user,
            Honor,
            {Honor.inh().name: ModifyDetail("set", raw_event["honor_type"])},
        )

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.group_upload")
    async def file_upload(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return

        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        user = group.member(str(raw_event["user_id"]))
        context = Context(account, group, user, group, group.member(str(self_id)))
        return FileReceived(
            context,
            group.file(raw_event["file"]["id"]),
        )
