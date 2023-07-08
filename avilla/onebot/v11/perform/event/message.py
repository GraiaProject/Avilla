from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.message import Message
from ...collector.connection import ConnectionCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived

from ...descriptor.event import OneBot11EventParse
from ...element import Reply

from loguru import logger

if TYPE_CHECKING:
    ...


class OneBot11EventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    @OneBot11EventParse.collect(m, "message.private.friend")
    async def private_friend(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        friend = Selector().land(account.route["land"]).friend(str(raw_event["sender"]["user_id"]))
        message = await self.protocol.deserialize_message(account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = friend.message(i[0].id)
            message = message.exclude(Reply)

        return MessageReceived(
            Context(
                account,
                friend,
                friend,
                friend,
                Selector().land(account.route["land"]).account(str(raw_event["self_id"])),
            ),
            Message(
                id=raw_event["message_id"],
                scene=friend,
                sender=friend,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @OneBot11EventParse.collect(m, "message.private.group")
    async def private_group(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event["sender"]["group_id"]))
        # 好像 ob11 本来没这个字段, 但 gocq 是有的, 不过嘛, 管他呢
        member = group.member(str(raw_event["sender"]["user_id"]))
        message = await self.protocol.deserialize_message(account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = member.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            Context(
                account,
                member,
                group,
                group,
                Selector().land(account.route["land"]).account(str(raw_event["self_id"])),
            ),
            Message(
                id=raw_event["message_id"],
                scene=group,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @OneBot11EventParse.collect(m, "message.group.normal")
    @OneBot11EventParse.collect(m, "message.group.notice")
    async def group(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        member = group.member(str(raw_event["sender"]["user_id"]))
        message = await self.protocol.deserialize_message(account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = group.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            Context(
                account,
                member,
                group,
                group,
                Selector().land(account.route["land"]).account(str(raw_event["self_id"])),
            ),
            Message(
                id=raw_event["message_id"],
                scene=group,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @OneBot11EventParse.collect(m, "message.private.other")
    async def private_other(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        stranger = Selector().land(account.route["land"]).stranger(str(raw_event["sender"]["user_id"]))
        message = await self.protocol.deserialize_message(account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = stranger.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            Context(
                account,
                stranger,
                stranger,
                stranger,
                Selector().land(account.route["land"]).account(str(raw_event["self_id"])),
            ),
            Message(
                id=raw_event["message_id"],
                scene=stranger,
                sender=stranger,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )

    @OneBot11EventParse.collect(m, "message.group.anonymous")
    async def group_anonymous(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} received message {raw_event}")
            return
        group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
        people = group.anonymous(str(raw_event["anonymous"]["flag"]))
        message = await self.protocol.deserialize_message(account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = group.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            Context(
                account,
                people,
                group,
                group,
                Selector().land(account.route["land"]).account(str(raw_event["self_id"])),
            ),
            Message(
                id=raw_event["message_id"],
                scene=group,
                sender=people,
                content=message,
                time=datetime.fromtimestamp(raw_event["time"]),
                reply=reply,
            ),
        )
