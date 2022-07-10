from creart import create
from graia.amnesia.builtins.aiohttp import AiohttpService
from graia.broadcast import Broadcast

from avilla.core import Avilla
from avilla.core.event.message import MessageReceived
from avilla.elizabeth.protocol import ElizabethProtocol

protocol = ElizabethProtocol()
broadcast = create(Broadcast)
avilla = Avilla(
    broadcast,
    [protocol],
    [AiohttpService()]
)

@broadcast.receiver(MessageReceived)
async def on_message_received(event: MessageReceived):
    print(event.message)

avilla.launch_manager.launch_blocking()
# Any problem?... in chinese.
# fk ms.
# well i push it.
# : finding refs within liveshare env...