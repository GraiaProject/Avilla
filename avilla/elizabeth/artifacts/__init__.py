from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.trait.context import bounds, fetch, get_artifacts
from avilla.core.trait.signature import CompleteRule
from avilla.elizabeth.resource import (
    ElizabethAudioResource,
    ElizabethImageResource,
    ElizabethResource,
)
from graia.amnesia.builtins.aiohttp import AiohttpClientInterface

if TYPE_CHECKING:
    from avilla.core.context import Context

with bounds("group"):
    get_artifacts().setdefault(CompleteRule("member"), "group.member")


@fetch(ElizabethImageResource)  # type: ignore
@fetch(ElizabethAudioResource)
async def fetch_from_url(cx: Context, res: ElizabethResource) -> bytes:
    if not res.url:
        raise NotImplementedError
    client = cx.avilla.launch_manager.get_interface(AiohttpClientInterface)
    return await (await client.request("GET", res.url)).io().read()
