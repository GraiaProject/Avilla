from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
from avilla.qqguild.collector.connection import ConnectionCollector
from avilla.qqguild.element import Reference
from avilla.standard.core.message import MessageReceived
from avilla.standard.core.message.event import MessageSent
from graia.amnesia.message import MessageChain, Text
from avilla.core.elements import Notice

if TYPE_CHECKING:
    ...

_ = {
    'author': {
        'avatar': 'https://qqchannel-profile-1251316161.file.myqcloud.com/1653330046467e135acaa82e17?t=1662709231', 
        'bot': False, 
        'id': '12813333378143120036', 
        'username': '不知道问RF'
    }, 
    'channel_id': '581493077', 
    'content': '<@!13480615970028680190> 4', 
    'guild_id': '13419678558140697107', 
    'id': '0893949c8fc5d1919eba0110d5c2a39502380a48d7f7d3a506',  # Message ID
    'member': {
        'joined_at': '2023-07-17T16:06:28+08:00', 
        'nick': '不知道问RF', 
        'roles': ['4', '12']
    }, 
    'mentions': [
        {
            'avatar': 'http://thirdqq.qlogo.cn/g?b=oidb&k=akFYgeY6XZoGG5iaAibyYggg&kti=ZLT72AAAAAA&s=0&t=1689581438', 
            'bot': True, 
            'id': '13480615970028680190', 
            'username': '渊白-测试中'
        }
    ], 
    'seq': 10, 
    'seq_in_channel': '10', 
    'timestamp': '2023-07-17T16:29:11+08:00'
}

class QQGuildEventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "at_message_create")
    async def at_message(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(self.connection.account_id)
        account = self.protocol.avilla.accounts.get(account_route)
        if account is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        guild = Selector().land("qqguild").guild(raw_event["guild_id"])
        channel = guild.channel(raw_event["channel_id"])
        author = channel.member(raw_event["author"]["id"])
        reply = None
        # if i := message.get(Reply):
        #     reply = friend.message(i[0].id)
        #     message = message.exclude(Reply)
        ats = [
            Notice(channel.user(i['id'])) for i in raw_event["mentions"]
        ]
        return MessageReceived(
            Context(
                account.account,
                author,
                channel,
                channel,
                account_route,
            ),
            Message(
                id=raw_event["id"],
                scene=channel,
                sender=author,
                # TODO: deserialize message
                content=MessageChain([*ats, Text(raw_event["content"])]),
                time=datetime.fromisoformat(raw_event["timestamp"]),
                reply=reply,
            ),
        )
    
    @EventParse.collect(m, "message_create")
    async def message(self, raw_event: dict):
        account_route = Selector().land("qqguild").account(self.connection.account_id)
        account = self.protocol.avilla.accounts.get(account_route)
        if account is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        guild = Selector().land("qqguild").guild(raw_event["guild_id"])
        channel = guild.channel(raw_event["channel_id"])
        author = channel.member(raw_event["author"]["id"])
        reply = None
        # if i := message.get(Reply):
        #     reply = friend.message(i[0].id)
        #     message = message.exclude(Reply)

        return MessageReceived(
            Context(
                account.account,
                author,
                channel,
                channel,
                account_route,
            ),
            Message(
                id=raw_event["id"],
                scene=channel,
                sender=author,
                # TODO: deserialize message
                content=MessageChain([Text(raw_event["content"])]),
                time=datetime.fromisoformat(raw_event["timestamp"]),
                reply=reply,
            ),
        )