from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageRevoke, MessageSend
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class OneBot11MessageActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.group")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        result = await self.account.call(
            "send_group_msg",
            {
                "group_id": int(target.pattern["group"]),
                "message": await self.account.staff.serialize_message(message),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['group']}: {message}")
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message(result["message_id"])

    @MessageRevoke.revoke.collect(m, "land.group.message")
    @MessageRevoke.revoke.collect(m, "land.friend.message")
    async def delete_msg(self, target: Selector):
        await self.account.call("delete_msg", {"message_id": int(target["message"])})

    @MessageSend.send.collect(m, "land.friend")
    async def send_friend_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        result = await self.account.call(
            "send_private_msg",
            {
                "user_id": int(target.pattern["friend"]),
                "message": await self.account.staff.serialize_message(message),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['friend']}: {message}")
        return (
            Selector().land(self.account.route["land"]).friend(target.pattern["friend"]).message(result["message_id"])
        )
