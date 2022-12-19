from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.builtins.aiohttp import AiohttpClientInterface

from avilla.core.abstract.trait.context import bounds, get_artifacts
from avilla.core.abstract.trait.recorder import fetch
from avilla.core.abstract.trait.signature import CompleteRule
from avilla.elizabeth.resource import ElizabethAudioResource, ElizabethImageResource

# from graia.amnesia.transport.common.http import AbstractClientInterface


if TYPE_CHECKING:
    from avilla.core.context import Context

# raise_for_no_namespace()

# Relationship Complete

# with scope("group"), prefix("group"):
#     completes("member", "group.member")
with bounds("group"):  # maybe problem
    get_artifacts().setdefault(CompleteRule("member"), "group.member")


@fetch(ElizabethImageResource)
@fetch(ElizabethAudioResource)
async def fetch_from_url(ctx: Context, res: ElizabethAudioResource | ElizabethImageResource) -> bytes:
    if not res.url:
        raise NotImplementedError
    # print(ctx.avilla.launch_manager._service_bind)
    client = ctx.avilla.launch_manager.get_interface(AiohttpClientInterface)
    # NOTE: wait for amnesia's fix on this.
    return await (await client.request("GET", res.url)).io().read()
