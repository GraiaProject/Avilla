from __future__ import annotations

from typing import TYPE_CHECKING

from graia.amnesia.transport.common.http import AbstractClientInterface
from graia.amnesia.builtins.aiohttp import AiohttpClientInterface

from avilla.core.traitof.context import prefix, raise_for_no_namespace, scope
from avilla.core.traitof.recorder import default_target, impl, pull, completes, fetch
from avilla.core.utilles.selector import Selector
from avilla.elizabeth.resource import ElizabethAudioResource, ElizabethImageResource, ElizabethResource

if TYPE_CHECKING:
    from avilla.core.relationship import Relationship

raise_for_no_namespace()

# Relationship Complete

with scope("group"), prefix("group"):
    completes("member", "group.member")


@fetch(ElizabethImageResource)
@fetch(ElizabethAudioResource)
async def fetch_from_url(rs: Relationship, res: ElizabethAudioResource | ElizabethImageResource) -> bytes:
    if not res.url:
        raise NotImplementedError
    print(rs.avilla.launch_manager._service_bind)
    client = rs.avilla.launch_manager.get_interface(AiohttpClientInterface)
    # NOTE: wait for amnesia's fix on this.
    return await client.request("GET", res.url).io().read()