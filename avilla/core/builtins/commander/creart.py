# pyright: reportMissingImports=false
from typing import Literal

from graia.broadcast import Broadcast

from . import Commander


def create_commander(module: Literal["graia.ariadne", "ichika"]) -> Commander:
    import creart

    broadcast = creart.it(Broadcast)

    if module == "graia.ariadne":
        from graia.ariadne.context import event_ctx
        from graia.ariadne.event.message import MessageEvent

        return Commander(broadcast, event_ctx, MessageEvent)

    elif module == "ichika":
        from ichika.graia import BROADCAST_EVENT
        from ichika.graia.event import MessageEvent

        return Commander(broadcast, BROADCAST_EVENT, MessageEvent)

    else:
        raise ValueError(f"Unknown module: {module}")
