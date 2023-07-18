from __future__ import annotations

from avilla.core.elements import Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.ryanvk.descriptor.message.deserialize import MessageDeserialize
from avilla.core.selector import Selector
from avilla.standard.qq.elements import Face

from ...element import Ark, ArkKv, Embed, Reference
from ...resource import QQGuildImageResource

QQGuildMessageDeserialize = MessageDeserialize[dict]


class QQGuildMessageDeserializePerform((m := ApplicationCollector())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @QQGuildMessageDeserialize.collect(m, "text")
    async def text(self, raw_element: dict) -> Text:
        return Text(raw_element["text"])

    @QQGuildMessageDeserialize.collect(m, "emoji")
    async def emoji(self, raw_element: dict) -> Face:
        return Face(raw_element["id"])

    @QQGuildMessageDeserialize.collect(m, "attachment")
    async def attachment(self, raw_element: dict) -> Picture:
        resource = QQGuildImageResource(Selector().land("qqguild").picture(url := raw_element["url"]), url)
        return Picture(resource)

    @QQGuildMessageDeserialize.collect(m, "mention")
    async def mention(self, raw_element: dict) -> Notice:
        if user_id := raw_element.get("user_id"):
            return Notice(Selector().land("qqguild").member(user_id))
        else:
            return Notice(Selector().land("qqguild").channel(raw_element["channel_id"]))

    @QQGuildMessageDeserialize.collect(m, "mention_everyone")
    async def mention_everyone(self, raw_element: dict) -> NoticeAll:
        return NoticeAll()

    @QQGuildMessageDeserialize.collect(m, "message_reference")
    async def message_reference(self, raw_element: dict) -> Reference:
        return Reference(raw_element["message_id"])

    @QQGuildMessageDeserialize.collect(m, "embed")
    async def embed(self, raw_element: dict) -> Embed:
        return Embed(
            raw_element.get("title"),
            raw_element.get("prompt"),
            raw_element.get("thumbnail", {})["url"],
            [i["name"] for i in raw_element.get("fields", [])],
        )

    @QQGuildMessageDeserialize.collect(m, "ark")
    async def ark(self, raw_element: dict) -> Ark:
        kvs: list[ArkKv] = []
        for i in raw_element.get("kv", []):
            if i.get("value"):
                kvs.append(ArkKv(**i))
            else:
                obj: list[dict] = [{slot["key"]: slot["value"] for slot in kv["obj_kv"]} for kv in i["obj"]]
                kvs.append(ArkKv(i["key"], obj=obj))
        return Ark(raw_element["template_id"], kvs)
