from __future__ import annotations

from datetime import timedelta
from typing import cast

from loguru import logger

from avilla.core.context import Context
from avilla.core.event import MetadataModified, ModifyDetail, RelationshipCreated, RelationshipDestroyed
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.onebot.v11.collector.connection import ConnectionCollector
from avilla.standard.core.activity import ActivityTrigged
from avilla.standard.core.privilege import MuteInfo, Privilege
from avilla.standard.qq.event import PocketLuckyKingNoticed
from avilla.standard.qq.honor import Honor


class OneBot11EventNoticePerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "notice.group_admin.set")
    async def group_admin_set(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))

        # get operator(group owner)
        members = await self.connection.call("get_group_member_list", {"group": raw["group_id"]})
        members = cast("list[dict]", members)
        operator_id = next((d["id"] for d in members if d["role"] == "owner"), None)
        operator = group.member(str(operator_id)) if operator_id else group
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return MetadataModified(
            context,
            endpoint,
            Privilege,
            {
                Privilege.inh(lambda x: x.available): ModifyDetail("update", True, False),
                Privilege.inh(lambda x: x.effective): ModifyDetail("update", True, False),
            },
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "notice.group_admin.unset")
    async def group_admin_unset(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))

        # get operator(group owner)
        members = await self.connection.call("get_group_member_list", {"group": raw["group_id"]})
        members = cast("list[dict]", members)
        operator_id = next((d["id"] for d in members if d["role"] == "owner"), None)
        operator = group.member(str(operator_id)) if operator_id else group
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return MetadataModified(
            context,
            endpoint,
            Privilege,
            {
                Privilege.inh(lambda x: x.available): ModifyDetail("update", False, True),
                Privilege.inh(lambda x: x.effective): ModifyDetail("update", False, True),
            },
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "notice.group_decrease.leave")
    async def member_leave(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))
        operator = group.member(str(raw["operator_id"]))
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return RelationshipDestroyed(context, True, True)

    @EventParse.collect(m, "notice.group_decrease.kick")
    async def member_kick(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))
        operator = group.member(str(raw["operator_id"]))
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return RelationshipDestroyed(context, False, True)

    @EventParse.collect(m, "notice.group_decrease.kick_me")
    async def member_kick_me(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))
        operator = group.member(str(raw["operator_id"]))
        context = Context(account, operator, endpoint, group, group.member(str(self_id)))
        return RelationshipDestroyed(context, False, False)

    @EventParse.collect(m, "notice.group_increase.approve")
    async def member_increase_approve(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))
        operator = group.member(str(raw["operator_id"]))
        context = Context(
            account,
            operator,
            endpoint,
            group,
            group.member(str(self_id)),
        )
        return RelationshipCreated(context)

    @EventParse.collect(m, "notice.group_increase.invite")
    async def member_increase_invite(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))
        operator = group.member(str(raw["operator_id"]))
        context = Context(account, operator, endpoint, group, group.member(str(self_id)), mediums=[group])
        return RelationshipCreated(context)

    @EventParse.collect(m, "notice.group_ban.ban")
    async def member_muted(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))
        operator = group.member(str(raw["operator_id"]))
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
                MuteInfo.inh(lambda x: x.muted): ModifyDetail("set", True),
                MuteInfo.inh(lambda x: x.duration): ModifyDetail("set", timedelta(seconds=raw["duration"])),
            },
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "notice.group_ban.lift_ban")
    async def member_unmuted(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        group = Selector().land("qq").group(str(raw["group_id"]))
        endpoint = group.member(str(raw["user_id"]))
        operator = group.member(str(raw["operator_id"]))
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
                MuteInfo.inh(lambda x: x.muted): ModifyDetail("clear"),
                MuteInfo.inh(lambda x: x.duration): ModifyDetail("clear"),
            },
            operator=operator,
            scene=group,
        )

    @EventParse.collect(m, "notice.friend_add")
    async def friend_add(self, raw: dict):
        self_id = raw["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw}")
            return
        friend = Selector().land("qq").friend(str(raw["user_id"]))
        context = Context(account, friend, friend, friend, account.route)
        return RelationshipCreated(context)

    @EventParse.collect(m, "notice.notify.poke")
    async def nudge_received(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return
        if "group_id" in raw_event:
            group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
            target = group.member(str(raw_event["target_id"]))
            operator = group.message(str(raw_event["user_id"]))
            context = Context(account, operator, target, group, group.member(str(self_id)))
            return ActivityTrigged(context, "nudge", group, target.nudge("_"), operator)
        else:
            friend = Selector().land(account.route["land"]).friend(str(raw_event["sender_id"]))
            selft = account.route
            context = Context(account, friend, selft, friend, selft)
            return ActivityTrigged(context, "nudge", friend, friend.nudge("_"), friend)

    @EventParse.collect(m, "notice.notify.lucky_king")
    async def lucky_king_received(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return

        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        target = group.member(str(raw_event["target_id"]))
        operator = group.message(str(raw_event["user_id"]))
        context = Context(account, operator, target, group, group.member(str(self_id)))
        return PocketLuckyKingNoticed(context)

    @EventParse.collect(m, "notice.notify.honor")
    async def honor(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return

        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        user = group.message(str(raw_event["user_id"]))
        context = Context(account, group, user, group, group.member(str(self_id)))
        return MetadataModified(
            context,
            user,
            Honor,
            {Honor.inh(lambda x: x.name): ModifyDetail("set", raw_event["honor_type"])},
        )
