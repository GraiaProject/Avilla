from __future__ import annotations

from datetime import datetime

from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.onebot.v11.collector.connection import ConnectionCollector
from avilla.onebot.v11.element import Reply
from avilla.standard.core.message import MessageReceived, MessageRevoked, MessageSent


class OneBot11EventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "message.private.friend")
    async def private_friend(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        friend = Selector().land(account.route["land"]).friend(str(raw_event["sender"]["user_id"]))
        context = Context(
            account,
            friend,
            friend,
            friend,
            Selector().land(account.route["land"]).account(str(raw_event["self_id"])),
        )
        message = await account.staff.ext({"context": context}).deserialize_message(raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = friend.message(i[0].id)
            message = message.exclude(Reply)

        return MessageReceived(
            context,
            Message(
                id=raw_event["message_id"],
                scene=friend,
                sender=friend,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @EventParse.collect(m, "message.private.group")
    async def private_group(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event["sender"]["group_id"]))
        # 好像 ob11 本来没这个字段, 但 gocq 是有的, 不过嘛, 管他呢
        member = group.member(str(raw_event["sender"]["user_id"]))
        context = Context(
            account,
            member,
            member,
            member,
            group.member(str(raw_event["self_id"])),
        )
        message = await account.staff.ext({"context": context}).deserialize_message(raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = member.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            context,
            Message(
                id=raw_event["message_id"],
                scene=member,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @EventParse.collect(m, "message.group.normal")
    @EventParse.collect(m, "message.group.notice")
    async def group(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        member = group.member(str(raw_event["sender"]["user_id"]))
        context = Context(
            account,
            member,
            group,
            group,
            group.member(str(raw_event["self_id"])),
        )
        message = await account.staff.ext({"context": context}).deserialize_message(raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = group.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            context,
            Message(
                id=raw_event["message_id"],
                scene=group,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @EventParse.collect(m, "message.private.other")
    async def private_other(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        stranger = Selector().land(account.route["land"]).stranger(str(raw_event["sender"]["user_id"]))
        context = Context(
            account,
            stranger,
            stranger,
            stranger,
            Selector().land(account.route["land"]).account(str(raw_event["self_id"])),
        )
        message = await account.staff.ext({"context": context}).deserialize_message(raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = stranger.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            context,
            Message(
                id=raw_event["message_id"],
                scene=stranger,
                sender=stranger,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @EventParse.collect(m, "message.group.anonymous")
    async def group_anonymous(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        people = group.anonymous(str(raw_event["anonymous"]["flag"]))
        context = Context(
            account,
            people,
            group,
            group,
            group.member(str(raw_event["self_id"])),
        )
        message = await account.staff.ext({"context": context}).deserialize_message(raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = group.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            context,
            Message(
                id=raw_event["message_id"],
                scene=group,
                sender=people,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @EventParse.collect(m, "message_sent.group.normal")
    async def message_sent(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return

        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        member = group.member(str(raw_event["user_id"]))
        context = Context(account, member, group, group, member)
        message = await account.staff.ext({"context": context}).deserialize_message(raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = member.message(i[0].id)
            message = message.exclude(Reply)
        return MessageSent(
            context,
            Message(
                str(raw_event["message_id"]),
                group,
                member,
                message,
                datetime.fromtimestamp(raw_event["time"]),
                reply,
            ),
            account,
        )

    @EventParse.collect(m, "notice.group_recall")
    async def group_message_recall(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return

        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        sender = group.member(str(raw_event["user_id"]))
        message = group.message(str(raw_event["message_id"]))
        operator = group.message(str(raw_event["operator_id"]))
        context = Context(account, operator, message, group, group.member(str(self_id)))
        return MessageRevoked(context, message, operator, sender)

    @EventParse.collect(m, "notice.friend_recall")
    async def friend_message_recall(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return

        friend = Selector().land(account.route["land"]).group(str(raw_event["friend_id"]))
        message = friend.message(str(raw_event["message_id"]))
        context = Context(account, friend, message, friend, account.route)
        return MessageRevoked(context, message, friend, friend)
