from __future__ import annotations

from datetime import timedelta

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from loguru import logger

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.collector.connection import ConnectionCollector
from avilla.standard.core.activity import ActivityAvailable


class QQAPIEventActivityPerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/qqapi::event"
    m.identify = "activity"

    @m.entity(QQAPICapability.event_callback, event_type="interaction_create")
    async def button_interaction(self, event_type: ..., raw_event: dict):
        account_route = Selector().land("qq").account(self.connection.account_id)
        info = self.protocol.avilla.accounts.get(account_route)
        if info is None:
            logger.warning(f"Unknown account {self.connection.account_id} received message {raw_event}")
            return
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        account = info.account
        if raw_event["chat_type"] == 3:
            guild = Selector().land("qq").guild(raw_event["guild_id"])
            channel = guild.channel(raw_event["channel_id"])
            author = channel.member(raw_event["data"]["resolved"]["user_id"])
            context = Context(
                account,
                author,
                channel.member(account_route["account"]),
                channel,
                channel.member(account_route["account"]),
            )
            activity = channel.button(f'{raw_event["data"]["button_id"]}#{raw_event["data"]["button_data"]}')
            await cache.set(
                f"qqapi/account({account_route['account']}):{channel}", raw_event["id"], timedelta(minutes=5)
            )
        elif raw_event["chat_type"] == 2:
            friend = Selector().land("qq").friend(raw_event["data"]["resolved"]["user_id"])
            context = Context(account, friend, account_route, friend, account_route)
            activity = friend.button(f'{raw_event["data"]["button_id"]}#{raw_event["data"]["button_data"]}')
            await cache.set(
                f"qqapi/account({account_route['account']}):{friend}", raw_event["id"], timedelta(minutes=5)
            )
        else:
            group = Selector().land("qq").group(raw_event["group_open_id"])
            member = group.member(raw_event["data"]["resolved"]["user_id"])
            context = Context(
                account,
                member,
                group,
                group,
                group.member(account_route["account"]),
            )
            activity = group.button(f'{raw_event["data"]["button_id"]}#{raw_event["data"]["button_data"]}')
            await cache.set(f"qqapi/account({account_route['account']}):{group}", raw_event["id"], timedelta(minutes=5))
        return ActivityAvailable(context, "button_interaction", context.scene, activity)
