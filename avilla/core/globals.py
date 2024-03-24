from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from graia.broadcast.utilles import Ctx

if TYPE_CHECKING:
    from avilla.core.application import Avilla
    from avilla.core.context import Context
    from avilla.core.protocol import BaseProtocol


AVILLA_CONTEXT_VAR: Ctx[Avilla] = Ctx("avilla")
PROTOCOL_CONTEXT_VAR: Ctx[BaseProtocol] = Ctx("protocol")
CONTEXT_CONTEXT_VAR: Ctx[Context] = Ctx("context")


def get_current_avilla() -> Avilla:
    avilla = AVILLA_CONTEXT_VAR.get(None)
    if avilla:
        return avilla
    protocol = PROTOCOL_CONTEXT_VAR.get(None)
    if protocol:
        return protocol.avilla
    context = CONTEXT_CONTEXT_VAR.get(None)
    if context:
        return context.protocol.avilla
    raise RuntimeError("no any current avilla")


def get_current_protocol():
    protocol = PROTOCOL_CONTEXT_VAR.get(None)
    if protocol:
        return protocol
    context = CONTEXT_CONTEXT_VAR.get(None)
    if context:
        return context.protocol
    raise RuntimeError("no any current protocol")


def require_context(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if CONTEXT_CONTEXT_VAR.get(None):
            return await func(*args, **kwargs)
        raise RuntimeError("no any current context")

    return wrapper
