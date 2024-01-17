from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core import Context
from avilla.core.message import Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.standard.core.message import MessageRevoke, MessageSend
from avilla.standard.core.message.event import MessageSent
from avilla.standard.qq.elements import Forward

if TYPE_CHECKING:
    from ...account import OneBot11Account  # noqa
    from ...protocol import OneBot11Protocol  # noqa


class OneBot11MessageActionPerform((m := AccountCollector["OneBot11Protocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11::action"
    m.identify = "message"

    @MessageSend.send.collect(m, target="land.group")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if message.has(Forward):
            return await self.send_group_forward_msg(target, message.get_first(Forward))
        result = await self.account.connection.call(
            "send_group_msg",
            {
                "group_id": int(target.pattern["group"]),
                "message": await OneBot11Capability(self.account.staff).serialize_chain(message),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['group']}: {message}")
        context = self.account.get_context(target.member(self.account.route["account"]))
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    result["message_id"],
                    target,
                    context.client,
                    message,
                    datetime.now(),
                ),
                self.account,
            )
        )
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message(result["message_id"])

    @MessageRevoke.revoke.collect(m, target="land.group.message")
    @MessageRevoke.revoke.collect(m, target="land.friend.message")
    async def delete_msg(self, target: Selector):
        await self.account.connection.call("delete_msg", {"message_id": int(target["message"])})

    @MessageSend.send.collect(m, target="land.friend")
    async def send_friend_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if message.has(Forward):
            return await self.send_friend_forward_msg(target, message.get_first(Forward))
        result = await self.account.connection.call(
            "send_private_msg",
            {
                "user_id": int(target.pattern["friend"]),
                "message": await OneBot11Capability(self.account.staff).serialize_chain(message),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['friend']}: {message}")
        context = Context(
            self.account,
            self.account.route,
            target,
            target,
            self.account.route,
        )
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    result["message_id"],
                    target,
                    context.client,
                    message,
                    datetime.now(),
                ),
                self.account,
            )
        )
        return (
            Selector().land(self.account.route["land"]).friend(target.pattern["friend"]).message(result["message_id"])
        )

    async def send_group_forward_msg(self, target: Selector, forward: Forward) -> Selector:
        data = []
        for node in forward.nodes:
            if node.mid:
                data.append({"type": "node", "data": {"id": node.mid["message"]}})
            elif node.content:
                data.append(
                    {
                        "type": "node",
                        "data": {
                            "name": node.name,
                            "uin": node.uid,
                            "time": str(int(node.time.timestamp())),
                            "content": await OneBot11Capability(self.account.staff).serialize_chain(node.content),
                        },
                    }
                )
        result = await self.account.connection.call(
            "send_group_forward_msg",
            {
                "group_id": int(target.pattern["group"]),
                "messages": data,
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['group']}: {forward}")
        context = self.account.get_context(target.member(self.account.route["account"]))
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    result["message_id"],
                    target,
                    context.client,
                    MessageChain([forward]),
                    datetime.now(),
                ),
                self.account,
            )
        )
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message(result["message_id"])

    async def send_friend_forward_msg(self, target: Selector, forward: Forward) -> Selector:
        data = []
        for node in forward.nodes:
            if node.mid:
                data.append({"type": "node", "data": {"id": node.mid["message"]}})
            elif node.content:
                data.append(
                    {
                        "type": "node",
                        "data": {
                            "name": node.name,
                            "uin": node.uid,
                            "time": str(int(node.time.timestamp())),
                            "content": await OneBot11Capability(self.account.staff).serialize_chain(node.content),
                        },
                    }
                )
        result = await self.account.connection.call(
            "send_private_forward_msg",
            {
                "user_id": int(target.pattern["friend"]),
                "messages": data,
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to send message to {target.pattern['friend']}: {forward}")
        context = Context(
            self.account,
            self.account.route,
            target,
            target,
            self.account.route,
        )
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    result["message_id"],
                    target,
                    context.client,
                    MessageChain([forward]),
                    datetime.now(),
                ),
                self.account,
            )
        )
        return (
            Selector().land(self.account.route["land"]).friend(target.pattern["friend"]).message(result["message_id"])
        )
