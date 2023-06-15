from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from graia.broadcast.utilles import Ctx

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.context import Context
    from avilla.core.protocol import BaseProtocol


cx_avilla: Ctx[Avilla] = Ctx("avilla")
cx_protocol: Ctx[BaseProtocol] = Ctx("protocol")
cx_context: Ctx[Context] = Ctx("context")


def get_current_avilla() -> Avilla:
    avilla = cx_avilla.get(None)
    if avilla:
        return avilla
    protocol = cx_protocol.get(None)
    if protocol:
        return protocol.avilla
    context = cx_context.get(None)
    if context:
        return context.protocol.avilla
    raise RuntimeError("no any current avilla")


def get_current_protocol():
    protocol = cx_protocol.get(None)
    if protocol:
        return protocol
    context = cx_context.get(None)
    if context:
        return context.protocol
    raise RuntimeError("no any current protocol")


def require_context(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if cx_context.get(None):
            return await func(*args, **kwargs)
        raise RuntimeError("no any current context")

    return wrapper
