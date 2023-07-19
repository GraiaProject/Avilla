from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.exceptions import ActionFailed
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.ryanvk.staff import Staff
from avilla.core.selector import Selector
# from avilla.red.utils import pro_serialize
from avilla.standard.core.message import MessageRevoke, MessageSend
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedMessageActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.group")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        #TODO: serialize message
        await self.account.call(
            "message::send",
            {
                "peer": {
                    "chatType": 2,
                    "peerUid": target.pattern["group"],
                    "guildId": None,
                },
                "elements": [
                    {
                        "elementType": 1,
                        "textElement": {
                            "content": str(message),
                        }
                    }
                ]
            }
        )
        return (
            Selector()
            .land(self.account.route["land"])
            .group(target.pattern["group"])
            .message("xxxx")
        )

