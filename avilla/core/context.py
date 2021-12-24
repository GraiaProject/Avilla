from typing import TYPE_CHECKING

from graia.broadcast.utilles import Ctx

if TYPE_CHECKING:
    from graia.broadcast.entities.event import Dispatchable

    from . import Avilla
    from .protocol import BaseProtocol
    from .relationship import Relationship

ctx_avilla: "Ctx[Avilla]" = Ctx("avilla")
ctx_protocol: "Ctx[BaseProtocol]" = Ctx("protocol")
ctx_relationship: "Ctx[Relationship]" = Ctx("relationship")
ctx_event: "Ctx[Dispatchable]" = Ctx("event")
