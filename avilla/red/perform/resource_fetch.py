from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import ClientSession

from avilla.core import Context
from avilla.core.ryanvk.collector.protocol import ProtocolCollector
from avilla.core.ryanvk.descriptor.fetch import Fetch
from avilla.red.resource import RedImageResource
from graia.ryanvk import OptionalAccess

if TYPE_CHECKING:
    from ..account import RedAccount  # noqa
    from ..protocol import RedProtocol  # noqa


class RedResourceFetchPerform((m := ProtocolCollector["RedProtocol"]())._):
    m.post_applying = True
    context: OptionalAccess[Context] = OptionalAccess()

    @Fetch.collect(m, RedImageResource)
    async def fetch_resource(self, resource: RedImageResource) -> bytes:
        if not resource.path or not resource.path.exists():
            try:
                async with ClientSession() as session:
                    async with session.get(resource.url) as resp:
                        return await resp.read()
            except Exception as e:
                if not self.context:
                    raise ValueError("Resource path is not set.") from e
                if TYPE_CHECKING:
                    assert isinstance(self.context.account, RedAccount)
                return await self.context.account.websocket_client.call_http(
                    "post",
                    "api/message/fetchRichMedia",
                    {
                        "msgId": list(self.context.cache["meta"].keys())[0].last_value,
                        "chatType": 2 if self.context.scene.last_key == "group" else 1,
                        "peerUid": self.context.scene.last_value,
                        "elementId": resource.elem,
                        "thumbSize": 0,
                        "downloadType": 2,
                    },
                    raw=True,
                )
        with resource.path.open("rb") as f:
            return f.read()
