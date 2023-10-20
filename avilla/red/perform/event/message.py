from __future__ import annotations

from datetime import datetime, timedelta

from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.red.capability import RedCapability
from avilla.red.collector.connection import ConnectionCollector
from avilla.red.utils import pre_deserialize
from avilla.standard.core.message import MessageReceived, MessageSent
from graia.amnesia.builtins.memcache import Memcache, MemcacheService


class RedEventMessagePerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/red::event"
    m.identify = "message"

    @m.entity(RedCapability.event_callback, event_type="message::recv")
    async def message(self,  event_type: ..., raw_event: dict):
        account = self.connection.account
        if account is None:
            logger.warning(f"Unknown account received message {raw_event}")
            return
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        reply = None
        if raw_event["chatType"] == 2:
            group = (
                Selector().land(account.route["land"]).group(str(raw_event.get("peerUin", raw_event.get("peerUid"))))
            )
            member = group.member(str(raw_event.get("senderUin", raw_event.get("senderUid"))))
            context = Context(
                account,
                member,
                group,
                group,
                group.member(account.route["account"]),
            )
            elements = pre_deserialize(raw_event["elements"])
            if elements[0]["type"] == "reply":
                reply = group.message(f"{elements[0]['sourceMsgIdInRecords']}")
                elements = elements[1:]
            message = await RedCapability(account.staff.ext({"context": context})).deserialize(
                elements
            )
            msg = Message(
                id=f'{raw_event["msgId"]}',
                scene=group,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(int(raw_event["msgTime"])),
                reply=reply,
            )
        else:
            friend = (
                Selector().land(account.route["land"]).friend(f"{raw_event.get('peerUin', raw_event.get('senderUin'))}")
            )
            context = Context(
                account,
                friend,
                account.route,
                friend,
                account.route,
            )
            elements = pre_deserialize(raw_event["elements"])
            if elements[0]["type"] == "reply":
                reply = friend.message(f"{elements[0]['sourceMsgIdInRecords']}")
                elements = elements[1:]
            message = await RedCapability(account.staff.ext({"context": context})).deserialize(
                elements
            )
            msg = Message(
                id=f'{raw_event["msgId"]}',
                scene=friend,
                sender=friend,
                content=message,
                time=datetime.fromtimestamp(int(raw_event["msgTime"])),
                reply=reply,
            )
        await cache.set(f"red/account({account.route['account']}).message({msg.id})", raw_event, timedelta(minutes=5))
        context._collect_metadatas(msg.to_selector(), msg)
        return MessageSent(
            context,
            msg,
            account
        ) if msg.sender.last_value == account.route["account"] else MessageReceived(
            context,
            msg
        )
