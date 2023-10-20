from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.red.resource import RedFileResource, RedImageResource, RedResource, RedVideoResource, RedVoiceResource

if TYPE_CHECKING:
    from ..account import RedAccount  # noqa
    from ..protocol import RedProtocol  # noqa


class RedResourceFetchPerform((m := ProtocolCollector["RedProtocol"]())._):
    m.namespace = "avilla.protocol/red::resource_fetch"

    @m.entity(CoreCapability.fetch, resource=RedResource)
    @m.entity(CoreCapability.fetch, resource=RedFileResource)
    @m.entity(CoreCapability.fetch, resource=RedImageResource)
    @m.entity(CoreCapability.fetch, resource=RedVoiceResource)
    @m.entity(CoreCapability.fetch, resource=RedVideoResource)  # type: ignore
    async def fetch_resource(self, resource: RedResource) -> bytes:
        if (
            isinstance(resource, (RedImageResource, RedVoiceResource, RedVideoResource))
            and resource.path
            and resource.path.exists()
        ):
            with resource.path.open("rb") as f:
                return f.read()
        if isinstance(resource, RedImageResource):
            with suppress(Exception):
                async with ClientSession() as session:
                    async with session.get(resource.url) as resp:
                        return await resp.read()
        if TYPE_CHECKING:
            assert isinstance(resource.ctx.account, RedAccount)
        return await resource.ctx.account.websocket_client.call_http(
            "post",
            "api/message/fetchRichMedia",
            {
                "msgId": list(resource.ctx.cache["meta"].keys())[0].last_value,
                "chatType": 2 if resource.ctx.scene.last_key == "group" else 1,
                "peerUid": resource.ctx.scene.last_value,
                "elementId": resource.elem,
                "thumbSize": 0,
                "downloadType": 2,
            },
            raw=True,
        )
