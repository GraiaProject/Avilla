from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from graia.broadcast.utilles import Ctx

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.context import Context
    from avilla.core.protocol import BaseProtocol


ctx_avilla: Ctx[Avilla] = Ctx("avilla")
ctx_protocol: Ctx[BaseProtocol] = Ctx("protocol")
ctx_context: Ctx[Context] = Ctx("context")


def get_current_avilla() -> Avilla:
    avilla = ctx_avilla.get()
    if avilla:
        return avilla
    protocol = ctx_protocol.get()
    if protocol:
        return protocol.avilla
    relationship = ctx_context.get()
    if relationship:
        return relationship.protocol.avilla
    raise RuntimeError("no any current avilla")


def get_current_protocol():
    protocol = ctx_protocol.get()
    if protocol:
        return protocol
    relationship = ctx_context.get()
    if relationship:
        return relationship.protocol
    raise RuntimeError("no any current protocol")


def require_context(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if ctx_context.get():
            return await func(*args, **kwargs)
        raise RuntimeError("no any current relationship")

    return wrapper
