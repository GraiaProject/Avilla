from __future__ import annotations

import random
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived, MessageRevoke, MessageSend, MessageSent
from avilla.core.elements import Text, Notice, NoticeAll, Picture
from avilla.standard.qq.elements import Forward, Node
from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedMessageActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

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

    @MessageSend.send.collect(m, "land.group")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if message.has(Forward):
            return await self.send_group_forward_msg(target, message.get_first(Forward))
        msg = await self.account.staff.serialize_message(message)
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
            event = await self.account.staff.ext({"connection": self.account.websocket_client}).parse_event(
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

    @MessageSend.send.collect(m, "land.friend")
    async def send_friend_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        msg = await self.account.staff.serialize_message(message)
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
            event = await self.account.staff.ext({"connection": self.account.websocket_client}).parse_event(
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

    @MessageRevoke.revoke.collect(m, "land.group.message")
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

    @MessageRevoke.revoke.collect(m, "land.friend.message")
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

    async def send_group_forward_msg(self, target: Selector, forward: Forward) -> Selector:
        if all(node.mid for node in forward.nodes):
            # TODO: use RedCapability to send forward message
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
                            "msgId": node.mid["message"],
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
        elems = []
        for elem in node.content:
            if isinstance(elem, Text):
                elems.append({"text": {"str": elem.text}})
            elif isinstance(elem, Notice):
                elems.append({"text": {"str": f"@{elem.target.last_value}"}})
            elif isinstance(elem, NoticeAll):
                elems.append({"text": {"str": "@全体成员"}})
            elif isinstance(elem, Picture):
                data = await self.account.staff.fetch_resource(elem.resource)
                resp = await self.account.websocket_client.call_http(
                    "multipart",
                    "api/upload",
                    {
                        "file": {
                            "value": data,
                            "content_type": None,
                            "filename": "file_image",
                        }
                    },
                )
                md5 = resp["md5"]
                file = Path(resp["ntFilePath"])
                pid = f"{{{md5[:8].upper()}-{md5[8:12].upper()}-{md5[12:16].upper()}-{md5[16:20].upper()}-{md5[20:].upper()}}}{file.suffix}"  # noqa: E501
                elems.append(
                    {
                        "customFace": {
                            "filePath": pid,
                            "fileId": random.randint(0, 65535),
                            "serverIp": -1740138629,
                            "serverPort": 80,
                            "fileType": 1001,
                            "useful": 1,
                            "md5": [int(md5[i : i + 2], 16) for i in range(0, 32, 2)],
                            "imageType": 1001,
                            "width": resp["imageInfo"]["width"],
                            "height": resp["imageInfo"]["height"],
                            "size": resp["fileSize"],
                            "origin": 0,
                            "thumbWidth": 0,
                            "thumbHeight": 0,
                            "pbReserve": [2, 0],
                        }
                    }
                )
            else:
                elems.append({"text": {"str": str(elem)}})
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
