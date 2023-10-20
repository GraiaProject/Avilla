from __future__ import annotations

import random
from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived, MessageRevoke, MessageSend, MessageSent
from avilla.red.capability import RedCapability
from avilla.standard.qq.elements import Forward, Node
from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedMessageActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.namespace = "avilla.protocol/red::action"
    m.identify = "message"


    async def handle_reply(self, target: Selector):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        reply_msg = await cache.get(
            f"red/account({self.account.route['account']}).message({target.pattern['message']})"
        )
        if reply_msg:
            return {
                "elementType": 7,
                "replyElement": {
                    "replayMsgId": reply_msg["msgId"],
                    "replayMsgSeq": reply_msg["msgSeq"],
                    "senderUin": reply_msg["senderUin"],
                    "senderUinStr": str(reply_msg["senderUin"]),
                },
            }
        logger.warning(f"Unknown message {target.pattern['message']} for reply")
        return None

    @m.entity(MessageSend.send, target="land.group")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if message.has(Forward):
            return await self.send_group_forward_msg(target, message.get_first(Forward))
        msg = await RedCapability(self.account.staff).serialize(message)
        if reply and (reply_msg := await self.handle_reply(reply)):
            msg.insert(0, reply_msg)
        resp = await self.account.websocket_client.call_http(
            "post",
            "api/message/send",
            {
                "peer": {
                    "chatType": 2,
                    "peerUin": target.pattern["group"],
                    "guildId": None,
                },
                "elements": msg,
            },
        )
        if "msgId" in resp:
            msg_id = resp["msgId"]
            event = await RedCapability(self.account.staff.ext({"connection": self.account.websocket_client})).event_callback(
                "message::recv", resp
            )
            if TYPE_CHECKING:
                assert isinstance(event, MessageReceived)
            event.context = self.account.get_context(target.member(self.account.route["account"]))
            event.message.scene = target
            event.message.sender = target.member(self.account.route["account"])
            self.protocol.post_event(MessageSent(event.context, event.message, self.account))
        else:
            msg_id = "unknown"
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message(msg_id)

    @m.entity(MessageSend.send, target="land.friend")
    async def send_friend_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        msg = await RedCapability(self.account.staff).serialize(message)
        if reply and (reply_msg := await self.handle_reply(reply)):
            msg.insert(0, reply_msg)
        resp = await self.account.websocket_client.call_http(
            "post",
            "api/message/send",
            {
                "peer": {
                    "chatType": 1,
                    "peerUin": target.pattern["friend"],
                    "guildId": None,
                },
                "elements": msg,
            },
        )
        if "msgId" in resp:
            msg_id = resp["msgId"]
            event = await RedCapability(self.account.staff.ext({"connection": self.account.websocket_client})).event_callback(
                "message::recv", resp
            )
            if TYPE_CHECKING:
                assert isinstance(event, MessageReceived)
            event.context = self.account.get_context(target, via=self.account.route)
            event.message.scene = target
            event.message.sender = self.account.route
            self.protocol.post_event(MessageSent(event.context, event.message, self.account))
        else:
            msg_id = "unknown"
        return Selector().land(self.account.route["land"]).friend(target.pattern["friend"]).message(msg_id)

    @m.entity(MessageRevoke.revoke, target="land.group.message")
    async def revoke_group_msg(
        self,
        target: Selector,
    ) -> None:
        await self.account.websocket_client.call_http(
            "post",
            "api/message/recall",
            {
                "peer": {
                    "chatType": 2,
                    "peerUid": target.pattern["group"],
                    "guildId": None,
                },
                "msgId": [target.pattern["message"]],
            },
        )

    @m.entity(MessageRevoke.revoke, target="land.friend.message")
    async def revoke_friend_msg(
        self,
        target: Selector,
    ) -> None:
        await self.account.websocket_client.call_http(
            "post",
            "api/message/recall",
            {
                "peer": {
                    "chatType": 1,
                    "peerUid": target.pattern["friend"],
                    "guildId": None,
                },
                "msgId": [target.pattern["message"]],
            },
        )

    @m.entity(RedCapability.send_forward, target="land.group")
    async def send_group_forward_msg(self, target: Selector, forward: Forward) -> Selector:
        if all(node.mid for node in forward.nodes):
            await self.account.websocket_client.call_http(
                "post",
                "api/message/unsafeSendForward",
                {
                    "dstContact": {
                        "chatType": 2,
                        "peerUid": target.pattern["group"],
                        "guildId": None,
                    },
                    "srcContact": {
                        "chatType": 2,
                        "peerUid": target.pattern["group"],
                        "guildId": None,
                    },
                    "msgInfos": [
                        {
                            "msgId": node.mid["message"],  # type: ignore
                            "senderShowName": node.name
                        } for node in forward.nodes
                    ]
                },
            )
            return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message("unknown")
        if all(node.content for node in forward.nodes):
            elems = []
            base_seq = random.randint(0, 65535)
            for node in forward.nodes:
                elems.append(await self.export_forward_node(base_seq, node, target))
                base_seq += 1
            await self.account.websocket_client.call_http(
                "post",
                "api/message/unsafeSendForward",
                {
                    "dstContact": {
                        "chatType": 2,
                        "peerUid": target.pattern["group"],
                        "guildId": None,
                    },
                    "srcContact": {
                        "chatType": 2,
                        "peerUid": target.pattern["group"],
                        "guildId": None,
                    },
                    "msgElements": elems,
                },
            )
            return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message("unknown")
        raise ValueError("Forward message must have at least one node with content or mid")

    async def export_forward_node(self, seq: int, node: Node, target: Selector):
        cap = RedCapability(self.account.staff)
        elems = [await cap.forward_export(elem) for elem in node.content]   # type: ignore
        return {
            "head": {
                "field2": node.uid,
                "field8": {
                    "field1": target.pattern["group"],
                    "field4": node.name,
                },
            },
            "content": {
                "field1": 82,
                "field4": random.randint(0, 4294967295),
                "field5": seq,
                "field6": int(node.time.timestamp()),
                "field7": 1,
                "field8": 0,
                "field9": 0,
                "field15": {"field1": 0, "field2": 0},
            },
            "body": {"richText": {"elems": elems}},
        }
