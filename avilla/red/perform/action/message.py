from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageRevoke, MessageSend
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedMessageActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.group")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        msg = await self.account.staff.serialize_message(message)
        await self.account.websocket_client.call(
            "message::send",
            {
                "peer": {
                    "chatType": 2,
                    "peerUid": target.pattern["group"],
                    "guildId": None,
                },
                "elements": msg,
            },
        )
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message("xxxx")

    @MessageSend.send.collect(m, "land.friend")
    async def send_friend_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        msg = await self.account.staff.serialize_message(message)
        await self.account.websocket_client.call(
            "message::send",
            {
                "peer": {
                    "chatType": 1,
                    "peerUid": target.pattern["friend"].split("|")[1],
                    "guildId": None,
                },
                "elements": msg,
            },
        )
        return Selector().land(self.account.route["land"]).friend(target.pattern["friend"]).message("xxxx")

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
                    "peerUid": target.pattern["friend"].split("|")[1],
                    "guildId": None,
                },
                "msgId": [target.pattern["message"]],
            },
        )
