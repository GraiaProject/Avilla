from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core import Context, Message
from avilla.core.elements import Reference
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend, MessageSent
from avilla.telegram.capability import TelegramCapability

if TYPE_CHECKING:
    from avilla.telegram.account import TelegramAccount  # noqa
    from avilla.telegram.protocol import TelegramProtocol  # noqa


class TelegramMessageActionPerform((m := AccountCollector["TelegramProtocol", "TelegramAccount"]())._):
    m.namespace = "avilla.protocol/telegram::action"
    m.identify = "message"

    @m.entity(MessageSend.send, target="land.chat")
    @m.entity(MessageSend.send, target="land.chat.thread")
    async def send_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        serialized = await TelegramCapability(self.account.staff).serialize(message)
        composed = self.compose_elements(serialized)

        if reply:
            _reply = reply.last_value
        elif ref := message.get(Reference):
            _reply = ref[0].message.last_value
        else:
            _reply = None

        for part in composed:
            part["data"]["chat_id"] = target.pattern["chat"]
            if _reply:
                part["data"]["reply_parameters"] = {"message_id": int(_reply)}
            if target.last_key == "thread":
                part["data"]["message_thread_id"] = int(target.pattern["thread"])
            await self.account.connection.call(part["api_name"], _file=part.get("file"), **part["data"])

        # TODO: finish this

        # result: list[TelegramMessage] = await self.account.instance.send(target, serialized)
        # d_result = [MessageFragment.decompose(m) for m in result]
        # if self.account.instance.config.reformat:
        #     # MediaGroup may be out of order
        #     d_result = [MessageFragment.sort(*[frag for frags in d_result for frag in frags])]
        # decomposed = [await TelegramCapability(self.account.staff).deserialize(frag) for frag in d_result]
        # sent_chain = decomposed[0]
        # for m in decomposed[1:]:
        #     sent_chain.extend(m)
        # context = Context(
        #     account=self.account,
        #     client=self.account.route,
        #     endpoint=target,
        #     scene=target,
        #     selft=self.account.route,
        # )
        # message_ids = ",".join(map(str, [m.message_id for m in result]))
        # event = MessageSent(
        #     context,
        #     Message(
        #         id=",".join(map(str, [m.message_id for m in result])),
        #         scene=target,
        #         sender=self.account.route,
        #         content=sent_chain,
        #         time=datetime.now(),
        #     ),
        #     self.account,
        # )
        # self.protocol.post_event(event)
        # return Selector().land(self.account.route["land"]).chat(target.pattern["chat"]).message(message_ids)

    def compose_elements(self, elements: list[dict]) -> list[dict]:
        composable = {"message": ["message"]}
        composed: list[dict] = []
        last_compose: str = ""
        last_element: dict = {}

        for element in elements:
            if not last_compose:
                last_compose = element["api_name"][4:].lower()
                last_element = element
                continue
            this_compose: str = element["api_name"][4:].lower()
            if last_compose in composable and this_compose in composable[last_compose]:
                last_element = getattr(self, f"compose_{this_compose}")(last_element, element)
            else:
                composed.append(last_element)
                last_compose = this_compose
                last_element = element

        composed.append(last_element)
        return composed

    @staticmethod
    def compose_message(last: dict, this: dict) -> dict:
        text = last["data"]["text"] + this["data"]["text"]
        entity_offset = len(last["data"]["text"].encode("utf-16be"))
        for entity in this["data"]["entities"]:
            entity["offset"] += entity_offset
        last["data"]["entities"].extend(this["data"]["entities"])
        last["data"]["text"] = text
        return last
