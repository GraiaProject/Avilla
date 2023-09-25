from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.core.ryanvk.descriptor.fetch import Fetch
from avilla.red.resource import RedFileResource, RedImageResource, RedResource, RedVideoResource, RedVoiceResource

if TYPE_CHECKING:
    from ..account import RedAccount  # noqa
    from ..protocol import RedProtocol  # noqa


class RedResourceFetchPerform((m := ProtocolCollector["RedProtocol"]())._):
    m.post_applying = True

    @Fetch.collect(m, RedResource)
    @Fetch.collect(m, RedFileResource)
    @Fetch.collect(m, RedImageResource)
    @Fetch.collect(m, RedVoiceResource)
    @Fetch.collect(m, RedVideoResource)
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
        return await self.context.account.websocket_client.call_http(
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
