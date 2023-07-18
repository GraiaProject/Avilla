from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from avilla.core.elements import Notice, NoticeAll, Picture, Text
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.descriptor.message.serialize import MessageSerialize
from avilla.qqguild.tencent.element import Ark, Embed, Reference
from avilla.qqguild.tencent.resource import QQGuildImageResource
from avilla.standard.qq.elements import Face

if TYPE_CHECKING:
    from ...account import QQGuildAccount  # noqa
    from ...protocol import QQGuildProtocol  # noqa

QQGuildMessageSerialize = MessageSerialize[dict]


class QQGuildMessageSerializePerform((m := AccountCollector["QQGuildProtocol", "QQGuildAccount"]())._):
    m.post_applying = True

    # LINK: https://github.com/microsoft/pyright/issues/5409

    @QQGuildMessageSerialize.collect(m, Text)
    async def text(self, element: Text) -> dict:
        return {"type": "text", "text": element.text}

    @QQGuildMessageSerialize.collect(m, Face)
    async def face(self, element: Face) -> dict:
        return {"type": "emoji", "id": element.id}

    @QQGuildMessageSerialize.collect(m, Notice)
    async def notice(self, element: Notice) -> dict:
        if element.target.last_key == "channel":
            return {"type": "mention_channel", "channel_id": element.target["channel"]}
        return {"type": "mention_user", "user_id": element.target["member"]}

    @QQGuildMessageSerialize.collect(m, NoticeAll)
    async def notice_all(self, element: NoticeAll) -> dict:
        return {"type": "mention_everyone"}

    @QQGuildMessageSerialize.collect(m, Picture)
    async def picture(self, element: Picture) -> dict:
        if isinstance(element.resource, QQGuildImageResource):
            return {"type": "attachment", "url": element.resource.url}
        return {"type": "local_iamge", "content": await self.account.staff.fetch_resource(element.resource)}

    @QQGuildMessageSerialize.collect(m, Reference)
    async def reference(self, element: Reference) -> dict:
        return {"type": "message_reference", **asdict(element)}

    @QQGuildMessageSerialize.collect(m, Embed)
    async def embed(self, element: Embed) -> dict:
        res = {
            "type": "embed",
            "title": element.title,
            "prompt": element.prompt,
            "thumbnail": {"url": element.thumbnail} if element.thumbnail else None,
            "fields": [{"name": i} for i in element.fields] if element.fields else None,
        }
        return {k: v for k, v in res.items() if v}

    @QQGuildMessageSerialize.collect(m, Ark)
    async def ark(self, element: Ark) -> dict:
        return {
            "type": "ark",
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
