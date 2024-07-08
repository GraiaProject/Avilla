from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from avilla.core.elements import Audio, Face, File, Notice, NoticeAll, Picture, Text, Video
from avilla.core.resource import LocalFileResource, RawResource, UrlResource
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.qqapi.capability import QQAPICapability
from avilla.qqapi.element import Ark, Embed, Keyboard, Markdown, Reference
from avilla.qqapi.resource import (
    QQAPIAudioResource,
    QQAPIImageResource,
    QQAPIVideoResource,
    QQAPIFileResource,
)
from avilla.qqapi.utils import escape

if TYPE_CHECKING:
    from avilla.qqapi.account import QQAPIAccount  # noqa
    from avilla.qqapi.protocol import QQAPIProtocol  # noqa


class QQAPIMessageSerializePerform((m := AccountCollector["QQAPIProtocol", "QQAPIAccount"]())._):
    m.namespace = "avilla.protocol/qqapi::message"
    m.identify = "serialize"

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @m.entity(QQAPICapability.serialize_element, element=Text)
    async def text(self, element: Text):
        return escape(element.text)

    @m.entity(QQAPICapability.serialize_element, element=Face)
    async def face(self, element: Face):
        return f"<emoji:{element.id}>"

    @m.entity(QQAPICapability.serialize_element, element=Notice)
    async def notice(self, element: Notice):
        if element.target.last_key == "channel":
            return f"<#{element.target['channel']}>"
        return f'<qqbot-at-user id="{element.target["member"]}" />'

    @m.entity(QQAPICapability.serialize_element, element=NoticeAll)
    async def notice_all(self, element: NoticeAll):
        return "<qqbot-at-everyone />"

    @m.entity(QQAPICapability.serialize_element, element=Picture)
    async def picture(self, element: Picture):
        if isinstance(element.resource, (QQAPIImageResource, UrlResource)):
            return "media", ("image", element.resource.url)
        if isinstance(element.resource, LocalFileResource):
            return "file_image", element.resource.file.read_bytes()
        if isinstance(element.resource, RawResource):
            return "file_image", element.resource.data
        return "file_image", await self.account.staff.fetch_resource(element.resource)

    @m.entity(QQAPICapability.serialize_element, element=Audio)
    async def audio(self, element: Audio):
        if isinstance(element.resource, (QQAPIAudioResource, UrlResource)):
            return "media", ("audio", element.resource.url)
        if isinstance(element.resource, LocalFileResource):
            return "file_audio", element.resource.file.read_bytes()
        if isinstance(element.resource, RawResource):
            return "file_audio", element.resource.data
        return "file_audio", await self.account.staff.fetch_resource(element.resource)

    @m.entity(QQAPICapability.serialize_element, element=Video)
    async def video(self, element: Video):
        if isinstance(element.resource, (QQAPIVideoResource, UrlResource)):
            return "media", ("video", element.resource.url)
        if isinstance(element.resource, LocalFileResource):
            return "file_video", element.resource.file.read_bytes()
        if isinstance(element.resource, RawResource):
            return "file_video", element.resource.data
        return "file_video", await self.account.staff.fetch_resource(element.resource)

    @m.entity(QQAPICapability.serialize_element, element=File)
    async def file(self, element: File):
        if isinstance(element.resource, (QQAPIFileResource, UrlResource)):
            return "media", ("file", element.resource.url)
        if isinstance(element.resource, LocalFileResource):
            return "file_file", element.resource.file.read_bytes()
        if isinstance(element.resource, RawResource):
            return "file_file", element.resource.data
        return "file_file", await self.account.staff.fetch_resource(element.resource)

    @m.entity(QQAPICapability.serialize_element, element=Reference)
    async def reference(self, element: Reference):
        return "message_reference", {
            "message_id": element.message["message"],
            "ignore_get_message_error": element.ignore_get_message_error,
        }

    @m.entity(QQAPICapability.serialize_element, element=Embed)
    async def embed(self, element: Embed):
        res = {
            "title": element.title,
            "prompt": element.prompt,
            "thumbnail": {"url": element.thumbnail} if element.thumbnail else None,
            "fields": [{"name": i} for i in element.fields] if element.fields else None,
        }
        return "embed", {k: v for k, v in res.items() if v}

    @m.entity(QQAPICapability.serialize_element, element=Ark)
    async def ark(self, element: Ark):
        return "ark", {
            "template_id": element.template_id,
            "kv": [
                (
                    {
                        "key": kv.key,
                        "obj": [{"obj_kv": [{"key": k, "value": v} for k, v in obj_kv.items()]} for obj_kv in kv.obj],
                    }
                    if kv.obj
                    else {"key": kv.key, "value": kv.value}
                )
                for kv in element.kv
            ]
            if element.kv
            else None,
        }

    @m.entity(QQAPICapability.serialize_element, element=Markdown)
    async def markdown(self, element: Markdown):
        if element.params:
            param = [{"key": k, "values": v} for k, v in element.params.items()]
        else:
            param = None
        return "markdown", {
            "content": element.content,
            "custom_template_id": element.custom_template_id,
            "params": param,
        }

    @m.entity(QQAPICapability.serialize_element, element=Keyboard)
    async def keyboard(self, element: Keyboard):
        content = {"rows": []}
        for row in element.content or []:
            buttons = {"buttons": []}
            for button in row:
                raw = asdict(button)
                raw["render_data"] = asdict(button.render_data)
                raw["action"] = asdict(button.action)
                raw["action"]["permission"] = asdict(button.action.permission)
                buttons["buttons"].append(raw)
            content["rows"].append(buttons)

        return "keyboard", {"id": element.id, "content": content}
