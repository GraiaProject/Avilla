from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.elements import (
    Audio,
    Face,
    File,
    Notice,
    NoticeAll,
    Picture,
    Text,
    Video,
)
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.element import Ark, ArkKv, Embed, Reference
from avilla.qqapi.resource import (
    QQAPIAudioResource,
    QQAPIFileResource,
    QQAPIImageResource,
    QQAPIVideoResource,
)
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from avilla.core.context import Context


class QQAPIMessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = "avilla.protocol/qqapi::message"
    m.identify = "deserialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409
    context: OptionalAccess[Context] = OptionalAccess()

    @m.entity(QQAPICapability.deserialize_element, raw_element="text")
    async def text(self, raw_element: dict) -> Text:
        return Text(raw_element["text"])

    @m.entity(QQAPICapability.deserialize_element, raw_element="emoji")
    async def emoji(self, raw_element: dict) -> Face:
        return Face(raw_element["id"])

    @m.entity(QQAPICapability.deserialize_element, raw_element="attachment")
    async def attachment(self, raw_element: dict):
        if "content_type" not in raw_element:
            resource = QQAPIImageResource(Selector().land("qqguild").picture(url := raw_element["url"]), "image", url)
            return Picture(resource)
        content_type = raw_element["content_type"].split("/")[0]
        if content_type == "file":
            resource = QQAPIFileResource(
                Selector().land("qqguild").file(url := raw_element["url"]),
                raw_element["content_type"],
                url,
                raw_element.get("filename"),
                raw_element.get("height"),
                raw_element.get("width"),
                raw_element.get("size"),
            )
            return File(resource)
        if content_type == "audio":
            resource = QQAPIAudioResource(
                Selector().land("qqguild").audio(url := raw_element["url"]),
                raw_element["content_type"],
                url,
                raw_element.get("filename"),
                raw_element.get("height"),
                raw_element.get("width"),
                raw_element.get("size"),
            )
            return Audio(resource)
        if content_type == "video":
            resource = QQAPIVideoResource(
                Selector().land("qqguild").video(url := raw_element["url"]),
                raw_element["content_type"],
                url,
                raw_element.get("filename"),
                raw_element.get("height"),
                raw_element.get("width"),
                raw_element.get("size"),
            )
            return Video(resource)
        resource = QQAPIImageResource(
            Selector().land("qqguild").picture(url := raw_element["url"]),
            raw_element["content_type"],
            url,
            raw_element.get("filename"),
            raw_element.get("height"),
            raw_element.get("width"),
            raw_element.get("size"),
        )
        return Picture(resource)

    @m.entity(QQAPICapability.deserialize_element, raw_element="mention_user")
    async def mention(self, raw_element: dict) -> Notice:
        if self.context:
            return Notice(self.context.scene.member(raw_element["user_id"]))
        return Notice(Selector().land("qqguild").member(raw_element["user_id"]))

    @m.entity(QQAPICapability.deserialize_element, raw_element="mention_channel")
    async def mention_channel(self, raw_element: dict) -> Notice:
        if self.context:
            return Notice(
                Selector().land("qqguild").guild(self.context.scene["guild"]).channel(raw_element["channel_id"])
            )
        return Notice(Selector().land("qqguild").channel(raw_element["channel_id"]))

    @m.entity(QQAPICapability.deserialize_element, raw_element="mention_everyone")
    async def mention_everyone(self, raw_element: dict) -> NoticeAll:
        return NoticeAll()

    @m.entity(QQAPICapability.deserialize_element, raw_element="message_reference")
    async def message_reference(self, raw_element: dict) -> Reference:
        if self.context:
            return Reference(self.context.scene.message(raw_element["message_id"]))
        return Reference(Selector().land("qqguild").message(raw_element["message_id"]))

    @m.entity(QQAPICapability.deserialize_element, raw_element="embed")
    async def embed(self, raw_element: dict) -> Embed:
        return Embed(
            raw_element["title"],
            raw_element.get("prompt"),
            raw_element.get("thumbnail", {})["url"],
            [i["name"] for i in raw_element.get("fields", [])],
        )

    @m.entity(QQAPICapability.deserialize_element, raw_element="ark")
    async def ark(self, raw_element: dict) -> Ark:
        kvs: list[ArkKv] = []
        for i in raw_element.get("kv", []):
            if i.get("value"):
                kvs.append(ArkKv(**i))
            else:
                obj: list[dict] = [{slot["key"]: slot["value"] for slot in kv["obj_kv"]} for kv in i["obj"]]
                kvs.append(ArkKv(i["key"], obj=obj))
        return Ark(raw_element["template_id"], kvs)
