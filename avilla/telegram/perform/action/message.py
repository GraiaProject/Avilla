from __future__ import annotations

from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import TYPE_CHECKING

from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain

from avilla.core import Message
from avilla.core.elements import Reference
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import (
    MessageEdit,
    MessageRevoke,
    MessageSend,
    MessageSent,
)
from avilla.telegram.capability import TelegramCapability
from avilla.telegram.exception import InvalidEditedMessage

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
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        serialized = await TelegramCapability(self.account.staff).serialize(message)
        composed = self.compose_elements(serialized)

        if reply:
            _reply = reply.last_value
        elif ref := message.get(Reference):
            _reply = ref[0].message.last_value
        else:
            _reply = None

        result = []
        for part in composed:
            part["data"]["chat_id"] = target.pattern["chat"]
            if _reply:
                part["data"]["reply_parameters"] = {"message_id": int(_reply)}
            if target.last_key == "thread":
                part["data"]["message_thread_id"] = int(target.pattern["thread"])
            result.append(await self.account.connection.call(part["api_name"], _file=part.get("file"), **part["data"]))

        for resp in result:
            context = self.account.staff.get_context(target)
            chain = await TelegramCapability(self.account.staff.ext({"context": context})).deserialize(resp["result"])
            sent_message = Message(
                id=resp["result"]["message_id"],
                scene=target,
                sender=target.member(self.account.route["account"]),
                content=chain,
                time=datetime.now(),
                reply=reply,
            )
            self.protocol.post_event(MessageSent(context, sent_message, self.account))
        if len(result) == 1:
            return target.message(str(result[0]["result"]["message_id"]))
        token = token_urlsafe(16)
        await cache.set(
            f"telegram/account({self.account.route['account']}).messages({token})", result, timedelta(minutes=5)
        )
        return target.message(token)

    def compose_elements(self, elements: list[dict]) -> list[dict]:
        composable = {"message": ["message"], "photo": ["message"]}
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
                last_element = getattr(self, f"compose_{last_compose}")(last_element, element)
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

    @staticmethod
    def compose_caption(last: dict, this: dict) -> dict:
        caption = last["data"].get("caption", "") + this["data"]["text"]
        entity_offset = len(last["data"].get("caption", "").encode("utf-16be"))
        for entity in this["data"]["entities"]:
            entity["offset"] += entity_offset
        last["data"].setdefault("caption_entities", []).extend(this["data"]["entities"])
        last["data"]["caption"] = caption
        return last

    def compose_photo(self, last: dict, this: dict) -> dict:
        if list(this["data"].keys())[0] == "text":
            return self.compose_caption(last, this)

    @m.entity(MessageRevoke.revoke, target="land.chat.message")
    @m.entity(MessageRevoke.revoke, target="land.chat.thread.message")
    async def revoke_message(self, target: Selector):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        if result := await cache.get(
            f"telegram/account({self.account.route['account']}).messages({target['message']})"
        ):
            await self.account.connection.call(
                "deleteMessages",
                chat_id=int(target.pattern["chat"]),
                message_ids=[int(msg["result"]["message_id"]) for msg in result],
            )
            return
        await self.account.connection.call(
            "deleteMessage", chat_id=int(target.pattern["chat"]), message_id=int(target.pattern["message"])
        )

    @m.entity(MessageEdit.edit, target="land.chat.message")
    @m.entity(MessageEdit.edit, target="land.chat.thread.message")
    async def edit_message(self, target: Selector, content: MessageChain):
        editable = ["message", "photo", "audio", "document", "video", "animation"]
        serialized = await TelegramCapability(self.account.staff).serialize(content)
        composed = self.compose_elements(serialized)

        if len(composed) > 1 or composed[0]["api_name"][4:].lower() not in editable:
            raise InvalidEditedMessage()

        # TODO: impl this
