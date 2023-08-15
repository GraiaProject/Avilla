from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.red.collector.connection import ConnectionCollector
from avilla.red.utils import pre_deserialize
from avilla.standard.core.message import MessageReceived
from graia.amnesia.builtins.memcache import Memcache, MemcacheService

if TYPE_CHECKING:
    ...


class RedEventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "message::recv")
    async def message(self, raw_event: dict):
        account = self.connection.account
        if account is None:
            logger.warning(f"Unknown account received message {raw_event}")
            return
        payload = raw_event[0]
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if payload["chatType"] == 2:
            group = Selector().land(account.route["land"]).group(str(payload["peerUid"]))
            member = group.member(str(payload.get("senderUin", payload.get("senderUid"))))
            context = Context(
                account,
                member,
                group,
                group,
                group.member(account.route["account"]),
            )
            elements = pre_deserialize(payload["elements"])
            reply = None
            if elements[0]["type"] == "reply":
                reply = group.message(f"{elements[0]['sourceMsgIdInRecords']}")
                elements = elements[1:]
            message = await account.staff.x({"context": context}).deserialize_message(elements)
            msg = Message(
                id=f'{payload["msgId"]}',
                scene=group,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(int(payload["msgTime"])),
                reply=reply,
            )
        else:
            friend = (
                Selector()
                .land(account.route["land"])
                .friend(
                    f"{payload.get('peerUin', payload.get('senderUin'))}|"
                    f"{payload.get('peerUid', payload.get('senderUid'))}"
                )
            )
            context = Context(
                account,
                friend,
                friend,
                friend,
                account.route,
            )
            elements = pre_deserialize(payload["elements"])
            reply = None
            if elements[0]["type"] == "reply":
                reply = friend.message(f"{elements[0]['sourceMsgIdInRecords']}")
                elements = elements[1:]
            message = await account.staff.x({"context": context}).deserialize_message(elements)
            msg = Message(
                id=f'{payload["msgId"]}',
                scene=friend,
                sender=friend,
                content=message,
                time=datetime.fromtimestamp(int(payload["msgTime"])),
                reply=reply,
            )
        await cache.set(f"qq/red:{payload['msgId']}", payload, timedelta(minutes=5))
        context.cache["meta"][msg.to_selector()] = {Message: msg}  # type: ignore
        return MessageReceived(
            context,
            msg,
        )
