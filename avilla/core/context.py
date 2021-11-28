from datetime import timedelta
from typing import TYPE_CHECKING, Union

from graia.broadcast.utilles import Ctx

from avilla.core.selectors import mainline, rsctx

if TYPE_CHECKING:
    from graia.broadcast.entities.event import Dispatchable

    from . import Avilla
    from .protocol import BaseProtocol
    from .relationship import Relationship

ctx_avilla: "Ctx[Avilla]" = Ctx("avilla")
ctx_protocol: "Ctx[BaseProtocol]" = Ctx("protocol")
ctx_relationship: "Ctx[Relationship]" = Ctx("relationship")
ctx_event: "Ctx[Dispatchable]" = Ctx("event")

ctx_rsexec_to: "Ctx[Union[mainline, rsctx]]" = Ctx("target")
ctx_rsexec_period: "Ctx[timedelta]" = Ctx("period")
