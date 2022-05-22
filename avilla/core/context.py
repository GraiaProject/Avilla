import functools
from typing import TYPE_CHECKING, Any, Dict

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

ctx_eventmeta: "Ctx[Dict[str, Any]]" = Ctx("eventmeta")


def get_current_avilla():
    avilla = ctx_avilla.get()
    if avilla:
        return avilla
    protocol = ctx_protocol.get()
    if protocol:
        return protocol.avilla
    relationship = ctx_relationship.get()
    if relationship:
        return relationship.protocol.avilla
    raise RuntimeError("no any current avilla")


def get_current_protocol():
    protocol = ctx_protocol.get()
    if protocol:
        return protocol
    relationship = ctx_relationship.get()
    if relationship:
        return relationship.protocol
    raise RuntimeError("no any current protocol")


def get_current_relationship():
    relationship = ctx_relationship.get()
    if relationship:
        return relationship
    raise RuntimeError("no any current relationship")


def require_relationship(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        relationship = ctx_relationship.get()
        if relationship:
            return await func(*args, **kwargs)
        raise RuntimeError("no any current relationship")

    return wrapper
