from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived

from ...descriptor.event import OneBot11EventParse
from ...element import Reply

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class OneBot11EventMessagePerform((m := ProtocolCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.post_applying = True

    @OneBot11EventParse.collect(m, "message.private.friend")
    async def private_friend(self, raw_event: dict):
        friend = Selector().land(self.account.route["land"]).friend(str(raw_event["sender"]["user_id"]))
        message = await self.protocol.deserialize_message(self.account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = friend.message(i[0].id)
            message = message.exclude(Reply)

        return MessageReceived(
            Context(
                self.account,
                friend,
                friend,
                friend,
                Selector().land(self.account.route["land"]).account(str(raw_event["self_id"])),
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
        group = Selector().land(self.account.route["land"]).group(str(raw_event["sender"]["group_id"]))
        # 好像 ob11 本来没这个字段, 但 gocq 是有的, 不过嘛, 管他呢
        member = group.member(str(raw_event["sender"]["user_id"]))
        message = await self.protocol.deserialize_message(self.account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = member.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            Context(
                self.account,
                member,
                group,
                group,
                Selector().land(self.account.route["land"]).account(str(raw_event["self_id"])),
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
        group = Selector().land(self.account.route["land"]).group(str(raw_event["group_id"]))
        member = group.member(str(raw_event["sender"]["user_id"]))
        message = await self.protocol.deserialize_message(self.account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = group.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            Context(
                self.account,
                member,
                group,
                group,
                Selector().land(self.account.route["land"]).account(str(raw_event["self_id"])),
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
        stranger = Selector().land(self.account.route["land"]).stranger(str(raw_event["sender"]["user_id"]))
        message = await self.protocol.deserialize_message(self.account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = stranger.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            Context(
                self.account,
                stranger,
                stranger,
                stranger,
                Selector().land(self.account.route["land"]).account(str(raw_event["self_id"])),
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
        group = Selector().land(self.account.route["land"]).group(str(raw_event["group_id"]))
        people = group.anonymous(str(raw_event["anonymous"]["flag"]))
        message = await self.protocol.deserialize_message(self.account, raw_event["message"])
        reply = None
        if i := message.get(Reply):
            reply = group.message(i[0].id)
            message = message.exclude(Reply)
        return MessageReceived(
            Context(
                self.account,
                people,
                group,
                group,
                Selector().land(self.account.route["land"]).account(str(raw_event["self_id"])),
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
